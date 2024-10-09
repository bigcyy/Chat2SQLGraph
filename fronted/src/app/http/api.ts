import axios from "./axios";

// 获取用户信息
export const getUserInfo = () => {
  return axios.get("/api/user/info");
};

// 注册
export const register = (data: API.RegisterFrom) => {
  return axios.post("/api/user/register", data);
};

// 登录
export const login = (data: API.LoginForm) => {
  return axios.post("/api/user/login", data);
};

// 更新token
export const refreshToken = () => {
  return axios.post("/api/user/token");
};

// ----------------设置----------------

// 连接数据源
export const connectDataSource = (data: API.DataSource) => {
  return axios.post("/api/setting/datasource", data);
};

// 获取数据源列表
export const getDatasourceList = () => {
  return axios.get("/api/setting/datasource");
};

// 删除数据源
export const deleteDataSource = (id: number) => {
  return axios.delete("/api/setting/datasource", {
    data: { datasource_id: id },
  });
};

// 获取表信息
export const getTableInfo = (datasource_id: number) => {
  return axios.get(`/api/setting/datasource/${datasource_id}/table_info`);
};
