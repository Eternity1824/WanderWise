/**
 * 根据笔记ID构建图片URL
 * @param noteId 笔记ID
 * @param imageIndex 图片索引，默认为0（第一张图片）
 * @returns 图片URL
 */
export const getNoteImageUrl = (noteId: string, imageIndex: number = 0): string => {
  // 直接从前端项目的 images 文件夹读取图片
  return `/images/${noteId}/${imageIndex}.jpg`;
};

/**
 * 获取笔记的封面图片URL
 * @param noteId 笔记ID
 * @returns 封面图片URL
 */
export const getNoteCoverImageUrl = (noteId: string): string => {
  return getNoteImageUrl(noteId, 0);
};

/**
 * 获取默认封面图片URL
 * @returns 默认封面图片URL
 */
export const getDefaultCoverImageUrl = (): string => {
  return '/images/default.jpg';
}; 