"""
分数核算功能使用示例
"""

def score_calculation_example():
    """分数核算功能使用示例"""
    
    print("📊 分数核算功能使用示例")
    print("=" * 50)
    
    print("\n🎯 功能说明:")
    print("教师可以根据选定的题目ID列表，自动计算学生的总分数")
    print("计算完成后，分数会自动保存到CourseSelection表中")
    
    print("\n📝 使用步骤:")
    
    print("\n1. 教师选择题目:")
    problem_ids = [5, 6, 7, 8]
    print(f"   选择的题目ID: {problem_ids}")
    
    print("\n2. 调用分数核算接口:")
    print("   POST /teacher/score/calculate")
    print("   请求体:")
    print("   {")
    print(f'     "problem_ids": {problem_ids}')
    print("   }")
    
    print("\n3. 系统处理流程:")
    print("   ✅ 验证教师身份")
    print("   ✅ 获取当前学期")
    print("   ✅ 查询教师的课程")
    print("   ✅ 获取选课学生列表")
    print("   ✅ 计算每个学生的正确答题数")
    print("   ✅ 按规则计算分数（每题10分，上限100分）")
    print("   ✅ 更新CourseSelection表的score字段")
    print("   ✅ 提交数据库事务")
    
    print("\n4. 分数计算规则:")
    print("   - 每道题目：10分")
    print("   - 分数上限：100分")
    print("   - 计算公式：min(正确题目数 × 10, 100)")
    
    print("\n5. 示例计算:")
    examples = [
        (2, 20),   # 答对2题
        (5, 50),   # 答对5题
        (8, 80),   # 答对8题
        (10, 100), # 答对10题
        (15, 100)  # 答对15题（超过上限）
    ]
    
    for correct_count, expected_score in examples:
        calculated_score = min(correct_count * 10, 100)
        print(f"   答对{correct_count:2d}题 → {calculated_score:3d}分")
    
    print("\n6. 响应示例:")
    print("   {")
    print('     "code": 200,')
    print('     "msg": "核算完成",')
    print('     "scorelist": [')
    print("       {")
    print('         "course_id": "03",')
    print('         "student_id": "20232251177",')
    print('         "student_name": "张三",')
    print('         "class": "软件2211班",')
    print('         "total_score": 85')
    print("       },")
    print("       {")
    print('         "course_id": "03",')
    print('         "student_id": "20232251178",')
    print('         "student_name": "李四",')
    print('         "class": "软件2211班",')
    print('         "total_score": 90')
    print("       }")
    print("     ]")
    print("   }")
    
    print("\n7. 数据库更新:")
    print("   CourseSelection表中的记录会被更新:")
    print("   | id | student_id | course_id | score |")
    print("   |----|------------|-----------|-------|")
    print("   | 1  | 1          | 03        | 85    |")
    print("   | 2  | 2          | 03        | 90    |")
    
    print("\n🔧 技术实现:")
    print("✅ 查询优化 - 一次查询获取选课记录和学生信息")
    print("✅ 直接更新 - 在ORM对象上直接设置score属性")
    print("✅ 事务管理 - 统一提交确保数据一致性")
    print("✅ 错误处理 - 完善的异常处理机制")
    
    print("\n📊 前端展示:")
    print("计算完成后，可以使用ECharts展示分数统计图表:")
    print("- 柱状图显示每个学生的分数")
    print("- 颜色分级表示不同分数段")
    print("- 交互提示显示详细信息")
    
    print("\n🎉 分数核算功能使用示例完成！")


def database_schema_info():
    """数据库表结构信息"""
    
    print("\n📋 相关数据库表结构:")
    print("=" * 50)
    
    print("\n1. CourseSelection表 (选课记录):")
    print("   | 字段名     | 类型    | 说明           |")
    print("   |-----------|---------|----------------|")
    print("   | id        | Integer | 主键           |")
    print("   | student_id| Integer | 学生ID(外键)   |")
    print("   | course_id | Integer | 课程ID(外键)   |")
    print("   | date_id   | String  | 日期ID         |")
    print("   | score     | Integer | 分数(核算结果) |")
    
    print("\n2. AnswerRecord表 (答题记录):")
    print("   | 字段名        | 类型     | 说明         |")
    print("   |--------------|----------|--------------|")
    print("   | answer_id    | Integer  | 主键         |")
    print("   | student_id   | Integer  | 学生ID       |")
    print("   | problem_id   | Integer  | 题目ID       |")
    print("   | is_correct   | Integer  | 是否正确     |")
    print("   | submit_time  | DateTime | 提交时间     |")
    
    print("\n3. 关联关系:")
    print("   CourseSelection.student_id → Student.id")
    print("   CourseSelection.course_id → Course.course_id")
    print("   AnswerRecord.student_id → Student.id")
    print("   AnswerRecord.problem_id → Problem.problem_id")


if __name__ == "__main__":
    score_calculation_example()
    database_schema_info()
