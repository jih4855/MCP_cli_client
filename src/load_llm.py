import requests
from src.memory import MemoryManager
import google.generativeai as genai
from openai import OpenAI

class LLM:
    def __init__(self, model, system_prompt, provider, api_key=None, api_base=None,session_id=None, max_context=20, mcp_manager=None):
        self.model = model
        self.system_prompt = system_prompt
        self.memory = MemoryManager()
        self.provider = provider
        self.api_key = api_key
        self.api_base = api_base
        self.session_id = session_id
        self.max_context = max_context
        self.mcp_manager = mcp_manager  # ← 추가!

    async def check_provider(self, user_input, tools=None):
        if self.provider.lower() == "ollama":
            return await self.chat_ollama(user_input, tools)
        elif self.provider.lower() == "gemini":
            return await self.chat_gemini(user_input, tools)
        elif self.provider.lower() == "openai":
            return await self.chat_openai(user_input, tools)
        else:
            raise ValueError(f"지원되지 않는 제공자: {self.provider}")

    async def chat_ollama(self, user_input, tools=None):
        """
        user_input: 사용자가 입력한 텍스트
        tools: MCP에서 가져온 도구 목록
        max_context: 컨텍스트로 사용할 최대 대화 개수
        """
        self.user_input = user_input
        # 최근 max_context개 대화만 가져오기
        history = self.memory.get_history(self.session_id)

        # 시스템 프롬프트 준비
        system_content = self.system_prompt
        
        # 최근 대화만 추가 (user/assistant 쌍으로 계산)
        if len(history) > self.max_context:
            history = history[-self.max_context:]

        # tools 정규화
        normalized_tools = _normalize_tools(tools)
        ollama_tools = []
        for tool in normalized_tools:
            ollama_tools.append({
                "name": tool["name"],
                "description": tool.get("description", ""),
                "inputSchema": tool.get("inputSchema", {})
            })

        try:
            print(f"Ollama 모델 사용: {self.model}")
            print(f"대화 기록: {len(history)}개")
           
            messages = [{"role": "system", "content": system_content}]
        # 이전 대화 기록 추가
            if history:
                for message in history:
                    messages.append({
                        "role": message["role"],
                        "content": message["content"]
                    })

            # 현재 사용자 입력 추가
            messages.append({"role": "user", "content": self.user_input})

            # 디버깅 정보
            print(f"🔍 디버그 - 메시지 개수: {len(messages)}")
        

            # Ollama API 호출
            payload = {
                "model": self.model,
                "messages": messages,  # ← prompt 대신 messages
                "tools": ollama_tools,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 4000
                }
            }

            print(f"🔍 디버그 - 페이로드: {payload}")
            response = requests.post(
                self.api_base,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["message"]["content"].strip()
        
                # 대화 기록에 새 메시지들 추가
                history.append({"role": "user", "content": self.user_input})
                history.append({"role": "assistant", "content": ai_response})
                self.memory.save_history(self.session_id, history)

                return ai_response
            else:
                print(f"Ollama API 오류: {response.status_code}")
                print(f"응답: {response.text}")
                return None
                
        except Exception as e:
            print(f"모델 실행 오류: {e}")
            return None

    async def chat_gemini(self, user_input, tools=None):
        # 최근 max_context개 대화만 가져오기
        history = self.memory.get_history(self.session_id)
        self.user_input = user_input
        # 최근 대화만 추가 (user/assistant 쌍으로 계산)
        if len(history) > self.max_context:
            history = history[-self.max_context:]

        # tools 정규화
        normalized_tools = _normalize_tools(tools)

        try: 
            print(f"Gemini 모델 사용: {self.model}")
            print(f"대화 기록: {len(history)}개")
            
            # API 키 설정
            genai.configure(api_key=self.api_key)
            
            # 모델 객체 생성
            model = genai.GenerativeModel(self.model)
            
            # 대화 기록을 포함한 전체 프롬프트 구성
            full_prompt = self.system_prompt + "\n\n"
            
            # 이전 대화 기록 추가
            if history:
                for message in history:
                    role = "사용자" if message["role"] == "user" else "AI"
                    full_prompt += f"{role}: {message['content']}\n"
            
            # 현재 사용자 입력 추가
            full_prompt += f"사용자: {self.user_input}\nAI: "
            
            # tools가 있다면 function calling 설정
            # print(f"🔍 tools 매개변수: {tools}")
            # print(f"🔍 normalized_tools: {normalized_tools}")
            # print(f"🔍 normalized_tools 길이: {len(normalized_tools) if normalized_tools else 0}")
            if normalized_tools:
                gemini_tools = []
                for tool in normalized_tools:
                    input_schema = tool.get("inputSchema", {})
                    print(f"🔍 도구 '{tool['name']}' inputSchema: {input_schema}")
                    # Gemini function calling 형식으로 변환
                    gemini_tools.append(
                        genai.protos.Tool(
                            function_declarations=[
                                genai.protos.FunctionDeclaration(
                                    name=tool["name"],
                                    description=tool.get("description", ""),
                                    parameters=genai.protos.Schema(
                                        type=genai.protos.Type.OBJECT,
                                        properties=_convert_to_protos_properties(input_schema),
                                        required=input_schema.get("required", [])
                                    )
                                )
                            ]
                        )
                    )
                # print(f"도구 포함: {len(gemini_tools)}개")

                # tools와 함께 생성
                response = model.generate_content(
                    full_prompt,
                    tools=gemini_tools
                )
                
                function_calls_part = []
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_calls_part.append(part.function_call)  # function_call 객체만 추가

                if function_calls_part:
                    try:
                        all_results = []
                        for tool_calling in function_calls_part:
                            tool_result = await self.mcp_manager.multi_execute_tool(
                                tool_calling.name,  # 이제 올바른 접근
                                _convert_proto_args_to_dict(tool_calling.args)
                            )
                            all_results.append(f"도구 '{tool_calling.name}': {tool_result}")
                            print(f"✅ 도구 '{tool_calling.name}' 실행 결과: {tool_result}")

                        # 모든 결과를 포함한 최종 응답
                        results_text = "\n".join(all_results)
                        final_prompt = f"{full_prompt}\n도구 실행 결과:\n{results_text}\n이를 바탕으로 자연스럽게 답변해주세요."
                        final_response = model.generate_content(final_prompt)
                        ai_response_text = final_response.candidates[0].content.parts[0].text.strip()

                    except Exception as e:
                        print(f"❌ 도구 실행 실패: {e}")
                        ai_response_text = f"도구 실행 중 오류가 발생했습니다: {e}"
                else:
                  # 도구 호출 없을 때
                  ai_response_text = response.candidates[0].content.parts[0].text.strip()

            else:
                # tools 없이 생성
                response = model.generate_content(full_prompt)
                print(f"🔍 response 구조: {type(response)}")
                print(f"🔍 candidates: {len(response.candidates) if response.candidates else 0}")
                ai_response_text = response.candidates[0].content.parts[0].text.strip()
                print("도구 없음")
            
            # 대화 기록에 새 메시지들 추가
            history.append({"role": "user", "content": self.user_input})
            history.append({"role": "assistant", "content": ai_response_text})
            self.memory.save_history(self.session_id, history)

            return ai_response_text
    
        except Exception as e:
            print(f"모델 실행 오류: {e}")
            return None

    def chat_openai(self, user_input, tools=None):
            """
            user_input: 사용자가 입력한 텍스트
            tools: MCP에서 가져온 도구 목록
            max_context: 컨텍스트로 사용할 최대 대화 개수
            """
            self.user_input = user_input        
            # 최근 max_context개 대화만 가져오기
            history = self.memory.get_history(self.session_id)
            
            # 최근 대화만 추가 (user/assistant 쌍으로 계산)
            if len(history) > self.max_context:
                history = history[-self.max_context:]
            
            # tools 정규화
            normalized_tools = _normalize_tools(tools)
            OpenAI_tools = []
            for tool in normalized_tools:
                OpenAI_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("inputSchema", {})
                    }
                })

            try: 
                print(f"OpenAI 모델 사용: {self.model}")
                print(f"대화 기록: {len(history)}개")
                # 시스템 프롬프트와 사용자 입력 결합
                messages = [{"role": "system", "content": self.system_prompt}]
                # 이전 대화 기록 추가
                if history:
                    for message in history:
                        messages.append({
                            "role": message["role"],
                            "content": message["content"]
                        })
            
                client = OpenAI(api_key=self.api_key)

                # messages 리스트 구성 (Ollama와 유사한 방식)
                messages = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": self.user_input}
                ]
                if tools:
                    print(f"도구 포함: {len(OpenAI_tools)}개")
                    response = client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=OpenAI_tools if tools else [],
                    )
                else:
                    print("도구 없음")
                    response = client.chat.completions.create(
                        model=self.model,
                        messages=messages
                    )

                ai_response = response.choices[0].message.content.strip()
                # 대화 기록에 새 메시지들 추가
                history.append({"role": "user", "content": self.user_input})
                history.append({"role": "assistant", "content": ai_response})
                self.memory.save_history(self.session_id, history)

                return ai_response
            
            except Exception as e:
                print(f"모델 실행 오류: {e}")
                return None




def _convert_to_protos_properties(input_schema):
    """JSON 스키마를 genai.protos.Schema properties로 변환"""
    if not input_schema or not isinstance(input_schema, dict):
        return {}

    properties = {}
    schema_props = input_schema.get("properties", {})

    for prop_name, prop_info in schema_props.items():
        prop_type = prop_info.get("type", "string")

        # 타입 매핑
        if prop_type == "string":
            proto_type = genai.protos.Type.STRING
            schema_obj = genai.protos.Schema(
                type=proto_type,
                description=prop_info.get("description", "")
            )
        elif prop_type == "integer":
            proto_type = genai.protos.Type.INTEGER
            schema_obj = genai.protos.Schema(
                type=proto_type,
                description=prop_info.get("description", "")
            )
        elif prop_type == "number":
            proto_type = genai.protos.Type.NUMBER
            schema_obj = genai.protos.Schema(
                type=proto_type,
                description=prop_info.get("description", "")
            )
        elif prop_type == "boolean":
            proto_type = genai.protos.Type.BOOLEAN
            schema_obj = genai.protos.Schema(
                type=proto_type,
                description=prop_info.get("description", "")
            )
        elif prop_type == "array":
            proto_type = genai.protos.Type.ARRAY
            # array의 items 처리
            items_info = prop_info.get("items", {"type": "string"})
            items_type = items_info.get("type", "string")

            if items_type == "string":
                items_proto_type = genai.protos.Type.STRING
            elif items_type == "integer":
                items_proto_type = genai.protos.Type.INTEGER
            elif items_type == "number":
                items_proto_type = genai.protos.Type.NUMBER
            else:
                items_proto_type = genai.protos.Type.STRING

            schema_obj = genai.protos.Schema(
                type=proto_type,
                description=prop_info.get("description", ""),
                items=genai.protos.Schema(type=items_proto_type)
            )
        else:
            proto_type = genai.protos.Type.STRING  # 기본값
            schema_obj = genai.protos.Schema(
                type=proto_type,
                description=prop_info.get("description", "")
            )

        properties[prop_name] = schema_obj

    return properties
  
def _convert_proto_args_to_dict(proto_args):
    """Protocol Buffers args를 Python dict로 변환 (개선된 버전)"""
    result = {}

    # MapComposite 타입 체크
    if hasattr(proto_args, 'items'):
        # MapComposite인 경우
        for key, value in proto_args.items():
            result[key] = _extract_proto_value(value)
        return result

    # RepeatedComposite인 경우 (기존 로직)
    if hasattr(proto_args, 'fields'):
        for field in proto_args.fields:
            key = field.key
            value_obj = field.value
            result[key] = _extract_proto_value(value_obj)
        return result

    # 직접 dict 변환 시도
    try:
        return dict(proto_args)
    except:
        return {}

def _extract_proto_value(value_obj):
      """Protocol Buffers 값 추출"""
      if hasattr(value_obj, 'string_value') and value_obj.HasField('string_value'):
          return value_obj.string_value
      elif hasattr(value_obj, 'number_value') and value_obj.HasField('number_value'):
          return value_obj.number_value
      elif hasattr(value_obj, 'bool_value') and value_obj.HasField('bool_value'):
          return value_obj.bool_value
      elif hasattr(value_obj, 'list_value') and value_obj.HasField('list_value'):
          # 배열 처리
          result = []
          for item in value_obj.list_value.values:
              result.append(_extract_proto_value(item))
          return result
      else:
          # 기본적으로 문자열 변환 시도
          return str(value_obj)

def _unwrap_tool(item):
    """튜플이면 두 번째 요소(tool)를 반환, 아니면 그대로 반환"""
    if isinstance(item, (tuple, list)) and len(item) == 2:
        return item[1]
    return item

def _get_tool_attr(tool, attr, default=None):
    """tool에서 속성을 안전하게 가져오기"""
    if isinstance(tool, dict):
        return tool.get(attr, default)
    return getattr(tool, attr, default)

def _normalize_tools(tools):
        if not tools:
            return []
        
        actual_tools = []
        for item in tools:
            if isinstance(item, (tuple, list)) and len(item) == 2 and item[0] == "tools":
                actual_tools.extend(item[1])
            else:
                actual_tools.append(item)

        normalized = []
        for tool in actual_tools:  # ← 각 도구마다 처리!
            name = _get_tool_attr(tool, "name")
            if name:
                description = _get_tool_attr(tool, "description", "")
                input_schema = (
                    _get_tool_attr(tool, "inputSchema", {}) or
                    _get_tool_attr(tool, "parameters", {}) or
                    _get_tool_attr(tool, "schema", {}) or
                    {}
                )

                normalized.append({
                    "name": name,
                    "description": description,
                    "inputSchema": input_schema
                })

        return normalized