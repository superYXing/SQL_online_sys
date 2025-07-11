import os
import requests
import json
from typing import Optional, AsyncGenerator
from sqlalchemy.orm import Session
from models import Problem, DatabaseSchema, AnswerRecord, Student


class AIService:
    def __init__(self):
        self.api_url = os.getenv("AI_API_URL", "https://api.siliconflow.cn/v1/chat/completions")
        self.api_key = os.getenv("AI_API_KEY")
        self.model = os.getenv("AI_MODEL", "Qwen/Qwen3-32B")
        self.enable_thinking = os.getenv("AI_ENABLE_THINKING", "false").lower() == "true"


    async def analyze_sql_answer_stream(
        self,
        problem_id: int,
        answer_content: str,
        student_id: str,  # 注意：这里是学号字符串，不是数据库主键
        db: Session
    ) -> AsyncGenerator[str, None]:
        """
        AI分析SQL答案（流式输出）

        Args:
            problem_id: 题目ID
            answer_content: 学生答案内容
            student_id: 学生学号（字符串）
            db: 数据库会话

        Yields:
            AI分析结果的文本片段
        """
        try:
            # 获取题目信息
            problem = db.query(Problem).filter(Problem.problem_id == problem_id).first()
            if not problem:
                yield "题目不存在，无法进行分析。"
                return

            # 根据学号获取学生信息
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                yield "学生信息不存在，无法进行分析。"
                return

            # 获取数据库模式信息
            schema = db.query(DatabaseSchema).filter(
                DatabaseSchema.schema_id == problem.schema_id
            ).first()

            # 获取学生最近的答题记录来判断是否正确（使用数据库主键）
            latest_answer = db.query(AnswerRecord).filter(
                AnswerRecord.student_id == student.id,  # 使用数据库主键
                AnswerRecord.problem_id == problem_id
            ).order_by(AnswerRecord.timestep.desc()).first()

            # 构建AI分析的prompt
            prompt = self._build_prompt(
                problem=problem,
                schema=schema,
                answer_content=answer_content,
                is_correct=(latest_answer.result_type == 0) if latest_answer else False
            )

            # 调用AI API进行流式分析
            async for chunk in self._call_ai_api_stream(prompt):
                yield chunk

        except Exception as e:
            yield f"AI分析服务暂时不可用，请稍后再试。错误信息：{str(e)}"
    
    def _build_prompt(
        self, 
        problem: Problem, 
        schema: Optional[DatabaseSchema], 
        answer_content: str, 
        is_correct: bool
    ) -> str:
        """构建AI分析的prompt"""
        
        # 基础信息
        schema_info = ""
        if schema:
            schema_info = f"""
数据库名称：{schema.schema_name}
建表语句：{schema.sql_schema}
"""
        
        problem_info = f"""
题目描述：
{problem.problem_content}


"""
        
        student_sql = f"""
学生提交的SQL：
{answer_content}
"""
        
        if is_correct:
            # 回答正确的情况
            prompt = f"""你是一个SQL教学助手，首先分析数据库建表语句和题目信息。学生提交了一个正确的SQL答案，请给出表扬,同时给出另一种解题方式开拓视野。

建表信息：{schema_info}
题目信息：{problem_info}
学生的sql语句：{student_sql}

请分析学生的SQL语句，给出以下内容：
1. 表扬学生的正确解答
2. 分析SQL语句的优点
3. 提供其他可能的SQL实现思路或优化建议
4. 鼓励学生继续学习

请用友好、鼓励的语调回复，控制在200字以内。"""
        else:
            # 回答错误的情况
            prompt = f"""你是一个SQL教学助手。学生提交了一个错误的SQL答案，请帮助分析错误原因并给出改进建议。

建表信息：{schema_info}
题目信息：{problem_info}
学生的sql语句：{student_sql}

请分析学生的SQL语句，给出以下内容：
1. 指出SQL语句中的错误
2. 解释错误的原因
3. 提供正确的解决思路
4. 给出具体的改进建议

请用耐心、教学的语调回复，控制在250字以内。"""
        
        return prompt
    
    def _call_ai_api(self, prompt: str) -> str:
        """调用AI API"""
        if not self.api_key:
            return "AI服务配置错误，请联系管理员。"
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2048,
            "temperature": 0.7
        }

        # 根据测试结果，QwQ-32B模型不支持 enable_thinking 参数
        # 只有特定模型才添加此参数
        if self.enable_thinking and "Qwen3" in self.model:
            payload["enable_thinking"] = self.enable_thinking
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=90  # 增加超时时间到90秒，适应QwQ模型
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    return "AI服务返回格式异常，请稍后再试。"
            else:
                return f"AI服务请求失败，状态码：{response.status_code}"
                
        except requests.exceptions.Timeout:
            return "AI服务响应超时，请稍后再试。"
        except requests.exceptions.RequestException as e:
            return f"AI服务连接失败：{str(e)}"
        except Exception as e:
            return f"AI服务异常：{str(e)}"

    async def _call_ai_api_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """调用AI API进行流式输出"""
        if not self.api_key:
            yield "AI服务配置错误，请联系管理员。"
            return

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 8192,
            "temperature": 0.7,
            "stream": True  # 启用流式输出
        }

        # 根据测试结果，QwQ-32B模型不支持 enable_thinking 参数
        # 只有特定模型才添加此参数
        if self.enable_thinking and "Qwen3" in self.model:
            payload["enable_thinking"] = self.enable_thinking

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=90,
                stream=True  # 启用流式响应
            )

            if response.status_code == 200:
                # 处理流式响应
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]  # 移除 'data: ' 前缀
                            if data_str.strip() == '[DONE]':
                                break
                            try:
                                data = json.loads(data_str)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
            else:
                yield f"AI服务请求失败，状态码：{response.status_code}"

        except requests.exceptions.Timeout:
            yield "AI服务响应超时，请稍后再试。"
        except requests.exceptions.RequestException as e:
            yield f"AI服务连接失败：{str(e)}"
        except Exception as e:
            yield f"AI服务异常：{str(e)}"


# 创建AI服务实例
ai_service = AIService()
