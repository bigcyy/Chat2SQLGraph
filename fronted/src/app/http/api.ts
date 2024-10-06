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

// 获取所有模型
export const getModels = () => {
  return axios.get("/api/setting/model");
};

// 根据id删除模型
export const deleteModelById = (id: string) => {
  return axios.delete(`/api/setting/model`, { data: { model_id: id } });
};

// 连接数据源
export const connectDataSource = (data: API.DataSource) => {
  return axios.post("/api/setting/datasource", data);
};

// 添加表信息
export const addTableInfo = (data: API.TableInfo) => {
  return axios.post("/api/setting/datasource/4/table_info", data);
};

// 根据id删除数据源
export const deleteDataSourceById = (id: string) => {
  return axios.delete("/api/setting/datasource", {
    data: { datasource_id: id },
  });
};

// 获取表名列表
export const getTableInfo = () => {
	return axios.get("/api/setting/datasource/7/remote_table_info")
}

// 添加表名列表
export const addTableNameList = (data: API.TbaleNameList) => {
	return axios.post("/api/setting/datasource/7/table_info", data)
}

