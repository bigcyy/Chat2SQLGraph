declare namespace Global {
  type SupportedLang = "en" | "zh";
  interface Dictionary {
    title: string;
    slider: {
      [key: string]: string;
    };
    recents: {
      [key: string]: string;
    };
    confirm: {
      [key: string]: string;
    };
    new: {
      [key: string]: string;
    };
    chat: {
      [key: string]: string;
    };
    setting: {
      [key: string]: string;
    };
    login: {
      [key: string]: string;
    };
  }
  interface ChatItem {
    role: "user" | "assistant";
    content: string | React.ReactNode;
    editable?: boolean;
    id?: string;
    createdAt: number;
  }

  interface ModelProvider {
    provider: string;
    name: string;
  }
}

declare namespace Recents {
  interface RecentsContentProps {
    t: Global.Dictionary;
  }
}

declare namespace New {
  interface FileItem {
    filename: string;
    url: string;
  }
}

declare namespace Chat {
  interface ChatContentProps {
    t: Global.Dictionary;
  }
}

declare namespace Login {
  interface LoginContentProps {
    t: Global.Dictionary;
  }

  interface LoginFrom {
    username: string;
    password: string;
  }
  interface RegisterFrom {
    nickname: string;
    username: string;
    password: string;
    re_password: string;
  }

  interface LoginProps {
    form: FormInstance<LoginFrom>;
    onLogin: (values: LoginFrom) => void;
    t: Global.Dictionary;
  }
  interface RegisterProps {
    form: FormInstance<RegisterFrom>;
    onRegister: (values: RegisterFrom) => void;
    t: Global.Dictionary;
  }
}

declare namespace Store {
  interface Model {
    id: number;
    name: string;
    model_name: string;
    provider: string;
    created_at: string;
  }
  interface Setting {
    modelProviders: Global.ModelProvider[];
    models: Model[];
    currentProvider: string;
    currentModelId: number;
  }
  interface SettingState {
    settings: Setting;
  }
  interface SettingAction {
    setModelProviders: (providers: Global.ModelProvider[]) => void;
    setModels: (models: Model[]) => void;
    setCurrentProvider: (provider: string) => void;
    setCurrentModelId: (modelId: number) => void;
  }

  interface User {
    id: number;
    email: string;
    avatar?: string;
    name: string;
  }
  interface UserState {
    user: User;
  }
  interface UserAction {
    setUser: (user: User) => void;
    setUserToLocal: (user: User) => void;
    getUserAvatarFromLocal: () => void;
    setOneUserInfoToLocal: <K extends keyof User>(
      key: K,
      value: User[K]
    ) => void;
  }

  interface Session {
    id: string;
    title: string;
    messages: Global.ChatItem[];
    createdAt: number;
  }
  interface SessionState {
    chatData: Session[];
    curMsg: string;
  }
  interface SessionAction {
    addMessage: (sessionId: string, message: Message) => void;
    deleteMessage: (id: string, messageId: string) => void;
    addSession: (id: string, title: string) => void;
    deleteSession: (id: string) => void;
    saveSessionToLocal: () => void;
    getSessionFromLocal: () => void;
    setCurMsg: (msg: string) => void;
    getSessionById: (id: string) => Session | undefined;
    getReversedChatData: () => Session[];
    renameSession: (id: string, title: string) => void;
  }

  interface Datasource {
    id: number;
    datasource_name: string;
    database_name: string;
    url: string;
    port: number;
  }

  interface TableDetail {
    id: number;
    name: string;
    ddl: string;
    summary: string;
    datasource_id: number;
  }

  interface DatasourceState {
    datasource: Datasource[];
    selectedDatasource: Datasource | null;
    selectedTableKeys: string[];
    tableInfo: TableDetail[];
  }
  interface DatasourceAction {
    setDatasource: (datasource: Datasource[]) => void;
    setSelectedDatasource: (datasource: Datasource) => void;
    setTableInfo: (tableInfo: TableDetail[]) => void;
    setSelectedTableKeys: (tableKeys: string[]) => void;
  }
  interface ChatHistoryItem {
    id: string;
    datasource_id: number;
    datasource_name?: string;
    user_demand: string;
    created_at: number;
  }
  interface ChatState {
    chatData: ChatItem[];
    curMsg: string;
    chatHistory: ChatHistoryItem[];
  }
  interface ChatAction {
    setChatData: (chatData: ChatItem[]) => void;
    setCurMsg: (curMsg: string) => void;
    setChatHistory: (chatHistory: ChatHistoryItem[]) => void;
  }
}

declare namespace API {
  interface LoginForm {
    username: string;
    password: string;
  }
  interface RegisterFrom {
    nickname: string;
    username: string;
    password: string;
    re_password: string;
  }
  interface DataSource {
    datasource_name: string;
    datasource_description: string;
    database_name: string;
    url: string;
    port: number;
    username: string;
    password: string;
  }
  interface AddTable {
    table_name_list: string[];
    model_id: number;
  }
  interface StartChatData {
    user_select_tables: string[];
    user_demand: string;
    model_id: number;
  }
  interface AddModel {
    name: string;
    model_name: string;
    provider: number;
    api_key: string;
    base_url: string;
    self_defined_model?: string;
  }
}
