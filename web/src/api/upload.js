import { upload } from './request'

export function uploadImage(filePath) {
  return upload('/upload', filePath, 'file')
}
