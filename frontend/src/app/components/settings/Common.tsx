import React from "react";
import { Select } from "antd";

import { useSettingStore } from "../../lib/store";

export default function Common({ t }: { t: Global.Dictionary }) {
  const { settings, setCurrentModelId } = useSettingStore();

  const handleModelChange = (model: { label: string; value: string }) => {
    setCurrentModelId(parseInt(model.value));
  };

  const handleModelProviderChange = (provider: {
    label: string;
    value: string;
  }) => {
    console.log(provider);
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
              defaultValue={settings.modelProviders[0]?.provider && ''}
              optionFilterProp="label"
              onChange={(_, option) =>
                handleModelProviderChange(
                  option as { label: string; value: string }
                )
              }
              options={settings.modelProviders.map((item) => ({
                label: item.name,
                value: item.provider,
              }))}
              showSearch
              style={{ width: "50%" }}
            ></Select>
          </div>

          <div className="flex items-center">
            <label className="w-1/2 text-sm font-medium text-gray-700">
              {t.setting.model}
            </label>
            <Select
              defaultValue={
                settings.models.find(
                  (item) => item.id === settings.currentModelId
                )?.name
              }
              optionFilterProp="label"
              onChange={(_, option) =>
                handleModelChange(option as { label: string; value: string })
              }
              options={settings.models.map((item) => ({
                label: item.name,
                value: item.id.toString(),
              }))}
              showSearch
              style={{ width: "50%" }}
            ></Select>
          </div>
        </div>
      </div>
    </>
  );
}
