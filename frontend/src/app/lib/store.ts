import { create } from "zustand";

export const useSettingStore = create<Store.SettingState & Store.SettingAction>(
  (set) => ({
    settings: {
      modelProviders: [],
      models: [],
      currentProvider: "",
      currentModelId: -1, // 存的是模型的value，而不是描述
    },
    setModelProviders: (providers: Global.ModelProvider[]) => {
      set((state) => ({
        settings: { ...state.settings, modelProviders: providers },
      }));
    },
    setModels: (models: Store.Model[]) => {
      set((state) => {
        // 按照创建时间排序，最新的在后面
        models = models.sort((a, b) => -b.created_at.localeCompare(a.created_at));
        return { settings: { ...state.settings, models: models } };
      });
    },
    setCurrentProvider: (provider: string) => {
      set((state) => ({
        settings: { ...state.settings, currentProvider: provider },
      }));
    },
    setCurrentModelId: (modelId: number) => {
      set((state) => ({
        settings: { ...state.settings, currentModelId: modelId },
      }));
    },
  })
);

export const useUserStore = create<Store.UserState & Store.UserAction>(
  (set) => ({
    user: {
      id: -1,
      email: "",
      avatar: "https://avatars.githubusercontent.com/u/71807854?s=8100&v=4",
      name: "",
    },

    setUserToLocal: (user: Store.User) => {
      localStorage.setItem("user", JSON.stringify(user));
      set((state) => ({ user: { ...state.user, ...user } }));
    },
    setUser: (user: Store.User) => {
      set((state) => ({ user: { ...state.user, ...user } }));
    },
    setOneUserInfoToLocal: (
      key: keyof Store.User,
      value: Store.User[keyof Store.User]
    ) => {
      set((state) => {
        const newUser = { ...state.user, [key]: value };
        localStorage.setItem("user", JSON.stringify(newUser));
        return { user: newUser };
      });
    },
    getUserAvatarFromLocal: () => {
      const user = localStorage.getItem("user");
      if (user) {
        set((state) => ({ ...state, ...JSON.parse(user) }));
      }
    },
  })
);

export const useDatasourceStore = create<
  Store.DatasourceState & Store.DatasourceAction
>((set) => ({
  datasource: [],
  selectedDatasource: null,
  tableInfo: [],
  selectedTableKeys: [],
  setDatasource: (datasource: Store.Datasource[]) => {
    set(() => ({ datasource: datasource }));
  },
  setSelectedDatasource: (datasource: Store.Datasource) => {
    set(() => ({ selectedDatasource: datasource }));
  },
  setTableInfo: (tableInfo: Store.TableDetail[]) => {
    set(() => ({ tableInfo: tableInfo }));
  },
  setSelectedTableKeys: (tableKeys: string[]) => {
    set(() => ({ selectedTableKeys: tableKeys }));
  },
}));

export const useChatStore = create<Store.ChatState & Store.ChatAction>(
  (set) => ({
    chatData: [],
    curMsg: "",
    chatHistory: [],
    setChatData: (chatData: Global.ChatItem[]) => {
      set(() => ({ chatData: chatData }));
    },
    setCurMsg: (curMsg: string) => {
      set(() => ({ curMsg: curMsg }));
    },
    setChatHistory: (chatHistory: Store.ChatHistoryItem[]) => {
      set(() => ({ chatHistory: chatHistory }));
    },
  })
);
