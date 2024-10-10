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

// ----------------数据源----------------

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

// 获取远端表信息
export const getRemoteTableInfo = (datasource_id: number) => {
  return axios.get(
    `/api/setting/datasource/${datasource_id}/remote_table_info`
  );
};

// 获取表信息
export const getTableInfo = (datasource_id: number) => {
  return axios.get(`/api/setting/datasource/${datasource_id}/table_info`);
};

// 添加表
export const addTablesPOST = (datasource_id: number, data: API.AddTable) => {
  return axios.post(
    `/api/setting/datasource/${datasource_id}/table_info`,
    data
  );
};

// 删除表
export const deleteTable = (datasource_id: number, table_info_ids: number[]) => {
  return axios.delete(`/api/setting/datasource/${datasource_id}/table_info`, {
    data: { table_info_ids },
  });
};

// ----------------对话----------------

// 创建session
export const createSession = (datasource_id: number) => {
  return axios.post(`/api/chat/${datasource_id}`);
};

// 对话 
export const chat = (datasource_id: string, chat_id: string, data: API.StartChatData) => {
  return fetch(`/api/chat/${datasource_id}/${chat_id}`, {
    method: "POST",
    body: JSON.stringify(data),
    headers: {
      "Content-Type": "application/json",
      "Authorization": `${localStorage.getItem("token")}`,
    },
  });
};

// 获取当前数据源所有聊天列表
export const getSessionList = (datasource_id: number) => {
  return axios.get(`/api/chat/${datasource_id}`);
};

export const getCurrentChat = (datasource_id: string, chat_id: string) => {
  return axios.get(`/api/chat/${datasource_id}/${chat_id}`);
};
