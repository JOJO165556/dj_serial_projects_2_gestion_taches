import axios from '@/api/axios'

export interface Friendship {
  id: number
  sender: {
    id: number
    username: string
    first_name: string
    last_name: string
  }
  receiver: {
    id: number
    username: string
    first_name: string
    last_name: string
  }
  status: 'pending' | 'accepted' | 'declined'
  created_at: string
}

export const getFriendships = async () => {
  const response = await axios.get('friends/')
  return response.data as Friendship[]
}

export const sendFriendRequest = async (receiverId: number) => {
  const response = await axios.post('friends/', { receiver_id: receiverId })
  return response.data
}

export const acceptFriendRequest = async (friendshipId: number) => {
  const response = await axios.post(`friends/${friendshipId}/accept/`)
  return response.data
}

export const declineFriendRequest = async (friendshipId: number) => {
  const response = await axios.post(`friends/${friendshipId}/decline/`)
  return response.data
}
