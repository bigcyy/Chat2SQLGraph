import { Tabs } from "antd";

import Common from "./Common";
import Deep from "./Deep";
import User from "./User";

export default function Setting({ t, defalutPage = "select" }: Setting.SettingProps) {
  // const [modelProviders, setModelProviders] = useState<Global.ModelProvider[]>([]);

  const items = [
    {
      key: "select",
      label: "模型选择",
      children: <Common t={t} />,
    },
    {
      key: "add",
      label: "模型添加",
      children: <Deep t={t} />,
    },
    {
      key: "user",
      label: "用户信息",
      children: <User t={t} />,
    },
  ];
  return (
    <div className="bg-white shadow-md rounded-lg md:max-w-[500px] max-md:w-[95vw] mx-auto text-gray-700 p-2 !w-full">
      <Tabs items={items} defaultActiveKey={defalutPage} />
    </div>
  );
}
