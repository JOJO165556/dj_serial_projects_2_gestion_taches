import axios from '@/api/axios'
import type { User } from '@/types/auth'

export const updateProfile = async (userId: number, data: Partial<User>): Promise<User> => {
    const response = await axios.patch(`/api/users/${userId}/`, data)
    return response.data
}

export const searchUsers = async (query: string): Promise<User[]> => {
    const response = await axios.get(`/api/users/?search=${query}`)
    return response.data
}
