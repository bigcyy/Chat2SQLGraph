import React from "react";
import { Input, Select } from "antd";

import { useSettingStore } from "../../lib/store";

export default function Common({ t }: { t: Global.Dictionary }) {
  const { settings, saveOneSettingToLocal } = useSettingStore();

  const handleModelChange = (model: Store.Model) => {
    saveOneSettingToLocal("currentDisplayModel", model.label);
    saveOneSettingToLocal("currentModel", model.value);
  };
  return (
    <>
      <div className="p-6">
        <div className="space-y-4">
          <div className="flex items-center">
            <label className="w-1/2 text-sm font-medium text-gray-700">
              模型类别
            </label>
            <Select
              defaultValue={"OpenAI"}
              optionFilterProp="label"
              // onChange={(_, option) => handleModelChange(option as Store.Model)}
              options={[
                { label: "OpenAI", value: "OpenAI" },
                { lable: "Claude", value: "Claude" },
              ]}
              showSearch
              style={{ width: "50%" }}
            ></Select>
          </div>

          <div className="flex items-center">
            <label className="w-1/2 text-sm font-medium text-gray-700">
              {t.setting.model}
            </label>
            <Select
              defaultValue={settings.currentDisplayModel}
              optionFilterProp="label"
              onChange={(_, option) => handleModelChange(option as Store.Model)}
              options={settings.models}
              showSearch
              style={{ width: "50%" }}
            ></Select>
          </div>

          <div className="flex items-center">
            <label className="w-1/2 text-sm font-medium text-gray-700">
              {t.setting.custom_model}
            </label>
            <div className="w-1/2 flex items-center">
              <Input
                type="text"
                value={settings.customerModels.join(",")}
                onChange={(e) =>
                  saveOneSettingToLocal(
                    "customerModels",
                    e.target.value.split(",").map((model) => model.trim())
                  )
                }
                placeholder="model1,model2,model3"
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
