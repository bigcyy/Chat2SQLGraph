import React, { useState } from "react";
import { Input, Modal } from "antd";

import { useSettingStore } from "../../lib/store";
import MarkdownRenderer from "../MarkdownRenderer";
import { FILE_POST_URL_DESC } from "@/app/lib/constant";

export default function Deep({ t }: { t: Global.Dictionary }) {
  const { settings, saveOneSettingToLocal } = useSettingStore();
  const [open, setOpen] = useState(false);

  return (
    <div className="p-6">
      <div className="space-y-4">
        <div className="flex items-center">
          <label className="w-1/2 text-sm font-medium text-gray-700">
            {t.setting.api_endpoint}
          </label>
          <div className="w-1/2 flex items-center">
            <Input
              onChange={(e) => saveOneSettingToLocal("baseUrl", e.target.value)}
              placeholder="https://api.openai.com/"
              value={settings.baseUrl}
            />
          </div>
        </div>

        <div className="flex items-center">
          <label className="w-1/2 text-sm font-medium text-gray-700">
            {t.setting.api_key}
          </label>
          <div className="w-1/2 flex items-center">
            <Input
              type="text"
              value={settings.APIKey}
              onChange={(e) => saveOneSettingToLocal("APIKey", e.target.value)}
              placeholder="sk-xxx"
            />
          </div>
        </div>
      </div>
      <Modal open={open} onCancel={() => setOpen(false)}>
        <MarkdownRenderer content={FILE_POST_URL_DESC} />
      </Modal>
    </div>
  );
}
