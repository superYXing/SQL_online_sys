import os
import requests
from typing import Optional
from sqlalchemy.orm import Session
from models import Problem, DatabaseSchema, AnswerRecord


class AIService:
    def __init__(self):
        self.api_url = os.getenv("AI_API_URL", "https://api.siliconflow.cn/v1/chat/completions")
        self.api_key = os.getenv("AI_API_KEY")
        
    def analyze_sql_answer(
        self, 
        problem_id: int, 
        answer_content: str, 
        student_id: int,
        db: Session
    ) -> str:
        """
        AI分析SQL答案
        
        Args:
            problem_id: 题目ID
            answer_content: 学生答案内容
            student_id: 学生ID
            db: 数据库会话
            
        Returns:
            AI分析结果
        """
        try:
            # 获取题目信息
            problem = db.query(Problem).filter(Problem.problem_id == problem_id).first()
            if not problem:
                return "题目不存在，无法进行分析。"
            
            # 获取数据库模式信息
            schema = db.query(DatabaseSchema).filter(
                DatabaseSchema.schema_id == problem.schema_id
            ).first()
            
            # 获取学生最近的答题记录来判断是否正确
            latest_answer = db.query(AnswerRecord).filter(
                AnswerRecord.student_id == student_id,
                AnswerRecord.problem_id == problem_id
            ).order_by(AnswerRecord.timestep.desc()).first()
            
            # 构建AI分析的prompt
            prompt = self._build_prompt(
                problem=problem,
                schema=schema,
                answer_content=answer_content,
                is_correct=latest_answer.is_correct if latest_answer else False
            )
            
            # 调用AI API
            ai_response = self._call_ai_api(prompt)
            
            return ai_response
            
        except Exception as e:
            return f"AI分析服务暂时不可用，请稍后再试。错误信息：{str(e)}"
    
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
数据库模式：{schema.schema_name}
数据库描述：{schema.schema_discription or '无描述'}
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
            prompt = f"""你是一个SQL教学助手，首先分析数据库模式和题目信息。学生提交了一个正确的SQL答案，请给出表扬,同时给出另一种解题方式开拓视野。

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
            "model": "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
            "stream": False,
            "max_tokens": 8192,
            "thinking_budget": 32768,
            "min_p": 0.05,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "stop": [],
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                self.api_url, 
                json=payload, 
                headers=headers,
                timeout=30
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


# 创建AI服务实例
ai_service = AIService()
