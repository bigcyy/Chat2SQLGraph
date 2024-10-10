// lib/axiosConfig.js

import axios, { InternalAxiosRequestConfig } from "axios";

const instance = axios.create({
  // baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000",
  timeout: 60000, // 请求超时时间设置为 10 秒
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// 请求拦截器
instance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 定义不需要 token 的路由列表
    const noTokenRequired = ['/api/user/register', '/api/user/login'];

    // 检查当前请求的 URL 是否在不需要 token 的列表中
    if (!noTokenRequired.includes(config.url || '')) {
      const token = localStorage.getItem("token");
      if (token) {
        config.headers["Authorization"] = `${token}`;
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
instance.interceptors.response.use(
  (response) => {
    // 对响应数据做点什么
    return response;
  },
  (error) => {
    // 对响应错误做点什么
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 未授权，可能需要重新登录
          console.log("Unauthorized, please login");
          // 这里可以添加重定向到登录页面的逻辑
          break;
        case 403:
          console.log("Forbidden");
          break;
        case 404:
          console.log("Not Found");
          break;
        case 500:
          console.log("Internal Server Error");
          break;
        default:
          console.log(`An error occurred: ${error.response.status}`);
      }
    } else if (error.request) {
      // 请求已经发出，但没有收到响应
      console.log("No response received");
    } else {
      // 设置请求时发生了一些事情，触发了错误
      console.log("Error", error.message);
    }
    return Promise.reject(error);
  }
);

export default instance;
