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
    content: string;
    id: string;
    createdAt: number;
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
    label: string; // 显示的名称
    value: string; // 实际的名称
  }
  interface Setting {
    baseUrl: string;
    APIKey: string;
    models: Model[];
    customerModels: string[];
    currentDisplayModel: string;
    currentModel: string;
    historyNum: number;
  }
  interface SettingState {
    settings: Setting;
  }
  interface SettingAction {
    getSettingFromLocal: () => void;
    saveSettingsToLocal: (setting: Setting) => void;
    saveOneSettingToLocal: <K extends keyof Setting>(
      key: K,
      value: Setting[K]
    ) => void;
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
    tableInfo: TableDetail[];
  }
  interface DatasourceAction {
    setDatasource: (datasource: Datasource[]) => void;
    setSelectedDatasource: (datasource: Datasource) => void;
    setTableInfo: (tableInfo: TableDetail[]) => void;
  }
  interface ChatState {
    chatData: ChatItem[];
    curMsg: string;
  }
  interface ChatAction {
    setChatData: (chatData: ChatItem[]) => void;
    setCurMsg: (curMsg: string) => void;
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
    datasource_id: number;
    chat_id: string;
  }
}
