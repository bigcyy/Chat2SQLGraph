import { create } from "zustand";
import { DEFAULT_MODEL_LIST } from "./constant";

export const useSettingStore = create<Store.SettingState & Store.SettingAction>(
  (set) => ({
    settings: {
      baseUrl: "",
      APIKey: "",
      models: [],
      customerModels: [],
      currentDisplayModel: "GPT-4o mini",
      currentModel: "gpt-4o-mini",
      historyNum: 5,
    },
    getSettingFromLocal: () => {
      const setting = localStorage.getItem("setting");
      if (setting) {
        set((state) => {
          const newSetting = {
            ...state.settings,
            ...JSON.parse(setting),
          } as Store.Setting;

          // 合并默认模型列表和用户自定义模型列表
          const customerModels = newSetting.customerModels
            .filter((model) => model.trim() !== "")
            .map((model) => ({ label: model, value: model }));

          // 添加customer model 并去重
          newSetting.models = newSetting.models
            .concat(customerModels)
            .concat(DEFAULT_MODEL_LIST)
            .filter(
              (model, index, self) =>
                index === self.findIndex((t) => t.value === model.value)
            )
            .sort((a, b) => a.value.localeCompare(b.value));
          localStorage.setItem("setting", JSON.stringify(newSetting));
          return { settings: newSetting };
        });
      } else {
        set((state) => {
          const newSetting = { ...state.settings, models: DEFAULT_MODEL_LIST };
          localStorage.setItem("setting", JSON.stringify(newSetting));
          return { settings: newSetting };
        });
      }
    },
    saveSettingsToLocal: (setting: Store.Setting) => {
      set((state) => {
        const newSetting = { ...state.settings, ...setting };
        localStorage.setItem("setting", JSON.stringify(newSetting));
        return { settings: newSetting };
      });
    },
    saveOneSettingToLocal: <K extends keyof Store.Setting>(
      key: K,
      value: Store.Setting[K]
    ) => {
      set((state) => {
        const newSetting = { ...state.settings, [key]: value };
        if (key === "customerModels") {
          const valueToAdd = (value as string[])
            .filter((model) => model.trim() !== "")
            .map((model) => ({ label: model, value: model }));
          newSetting.models = DEFAULT_MODEL_LIST.concat(valueToAdd).filter(
            (model, index, self) =>
              index === self.findIndex((t) => t.value === model.value)
          );
        }
        localStorage.setItem("setting", JSON.stringify(newSetting));
        return { settings: newSetting };
      });
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

export const useDatasourceStore = create<Store.DatasourceState & Store.DatasourceAction>(
  (set) => ({
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
  })
);

export const useChatStore = create<Store.ChatState & Store.ChatAction>(
  (set) => ({
    chatData: [],
    curMsg: "",
    setChatData: (chatData: Global.ChatItem[]) => {
      set(() => ({ chatData: chatData }));
    },
    setCurMsg: (curMsg: string) => {
      set(() => ({ curMsg: curMsg }));
    },
  })
);

