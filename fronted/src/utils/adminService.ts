import axios from './axios'
import { ElMessage } from 'element-plus'

/**
 * 管理员服务 - 提供管理员和教师共用的API接口
 */
export class AdminService {
  /**
   * 删除学生
   * @param studentId 学生ID
   * @returns Promise<boolean> 删除是否成功
   */
  static async deleteStudent(studentId: string): Promise<boolean> {
    try {
      const response = await axios.delete(`/teacher/students/${studentId}`)
      
      if (response.data && response.data.success) {
        // 优先显示后端返回的message，如果没有则使用msg或默认消息
        const successMessage = response.data.message || response.data.msg || '删除成功'
        ElMessage.success(successMessage)
        return true
      } else {
        const errorMessage = response.data?.message || response.data?.msg || '删除失败'
        ElMessage.error(errorMessage)
        return false
      }
    } catch (error: any) {
      console.error('删除学生失败:', error)
      
      // 处理API错误响应
      if (error.response && error.response.data) {
        const errorMessage = error.response.data.message || error.response.data.msg || '删除失败'
        ElMessage.error(errorMessage)
      } else {
        ElMessage.error('删除失败，请稍后重试')
      }
      return false
    }
  }

  /**
   * 批量删除学生
   * @param studentIds 学生ID数组
   * @returns Promise<boolean> 删除是否成功
   */
  static async deleteStudents(studentIds: string[]): Promise<boolean> {
    try {
      const promises = studentIds.map(id => this.deleteStudent(id))
      const results = await Promise.all(promises)
      
      // 检查是否所有删除操作都成功
      const allSuccess = results.every(result => result === true)
      
      if (allSuccess) {
        ElMessage.success(`成功删除 ${studentIds.length} 名学生`)
      } else {
        ElMessage.warning('部分学生删除失败，请检查是否存在关联记录')
      }
      
      return allSuccess
    } catch (error) {
      console.error('批量删除学生失败:', error)
      ElMessage.error('批量删除失败')
      return false
    }
  }
}

// 导出默认实例
export default AdminService