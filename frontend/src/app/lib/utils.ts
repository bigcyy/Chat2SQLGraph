/**
 * 防抖
 * @param func 需要防抖的函数
 * @param wait 等待时间(毫秒)
 * @returns 防抖后的函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return function (...args: Parameters<T>) {
    if (timeout !== null) {
      clearTimeout(timeout);
    }

    timeout = setTimeout(() => {
      func(...args);
    }, wait);
  };
}

/**
 * 节流
 * @param func 需要节流的函数
 * @param limit 时间限制(毫秒)
 * @returns 节流后的函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false;

  return function (...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

export const all = async (arr: any[]) => {
  return new Promise((resolve, reject) => {
    let length = arr && arr.length;
    let count = 0;
    let result: any[] = [];
    if (!arr || arr.length === 0) {
      resolve(result);
    }
    arr.forEach(async (item, index) => {
      try {
        const res = await item;
        result[index] = res;
        count++;
        if (count === length) {
          resolve(result);
        }
      } catch (err) {
        reject(err);
      }
    });
  });
};
