import React, { useState, useEffect, useCallback } from "react";
import { Button, Form, Input, message, Select, Spin } from "antd";

import { useSettingStore } from "../../lib/store";
import { addModel, getModelsByProvider, testModel } from "../../http/api";

interface ModelOfProvider {
  name: string;
  desc: string;
}

export default function Deep({ t }: { t: Global.Dictionary }) {
  const [loading, setLoading] = useState(false);
  const { settings, setModels } = useSettingStore();
  const [modelsOfProvider, setModelsOfProvider] = useState<ModelOfProvider[]>(
    []
  );
  const [addModelForm] = Form.useForm<API.AddModel>();
  const [showSelfDefinedModel, setShowSelfDefinedModel] = useState(false);
  useEffect(() => {
    getModels(settings.currentProvider);
  }, []);

  const getModels = useCallback(async (provider: string) => {
    const res = (await getModelsByProvider(provider)).data;
    if (res.code === 200) {
      setModelsOfProvider(res.data);
    }
  }, []);

  const handleAddModel = async (values: API.AddModel) => {
    setLoading(true);
    
    values.base_url =
      values.base_url.slice(-1) === "/"
        ? values.base_url + "v1"
        : values.base_url + "/v1";
    let data = (await addModel(values)).data;
    if (data.code === 200) {
      message.success("添加成功");
      setModels([...settings.models, data.data]);
      addModelForm.resetFields();
      setShowSelfDefinedModel(false);
    } else {
      message.error(data.message);
    }
    setLoading(false);
  };

  const handleTestModel = async () => {
    try {
      setLoading(true);
      await addModelForm.validateFields();
      let values = addModelForm.getFieldsValue();
      if (values.model_name === "self-defined") {
        values.model_name = values.self_defined_model!;
        delete values.self_defined_model;
      }
      const { name, ...testValues } = values;
      testValues.base_url =
        testValues.base_url.slice(-1) === "/"
          ? testValues.base_url + "v1"
          : testValues.base_url + "/v1";
      const data = (await testModel(testValues)).data;
      if (data.code === 200) {
        message.success("测试成功");
      } else {
        message.error(data.message);
      }
      setLoading(false);
    } catch (error) {
      setLoading(false);
      return;
    }
  };

  const handleModelProviderChange = (option: {
    label: string;
    value: string;
  }) => {
    console.log(option);
    // getModels(provider);
  };

  const handleModelChange = (option: { label: string; value: string }) => {
    if (option.value === "self-defined") {
      setShowSelfDefinedModel(true);
    } else {
      setShowSelfDefinedModel(false);
    }
  };

  return (
    <div className="p-6">
      <Spin spinning={loading}>
        <div className="">
          <Form
            form={addModelForm}
            className="space-y-4"
            initialValues={{
              provider: settings.modelProviders[0].provider,
              model_name: settings.models[0].model_name,
            }}
            onFinish={handleAddModel}
          >
            <div className="flex items-center">
              <label className="w-1/2 text-sm font-medium text-gray-700">
                模型类别
              </label>
              <div className="w-1/2 flex items-center">
                <Form.Item
                  name="provider"
                  rules={[{ required: true, message: "请选择模型类别" }]}
                  className="w-full !mb-0"
                >
                  <Select
                    optionFilterProp="label"
                    onChange={(_, option) =>
                      handleModelProviderChange(
                        option as {
                          label: string;
                          value: string;
                        }
                      )
                    }
                    options={settings.modelProviders.map((item) => ({
                      label: item.name,
                      value: item.provider,
                    }))}
                    showSearch
                    style={{ width: "100%" }}
                  ></Select>
                </Form.Item>
              </div>
            </div>
            <div className="flex items-center">
              <label className="w-1/2 text-sm font-medium text-gray-700">
                {"模型名"}
              </label>
              <div className="w-1/2 flex items-center">
                <Form.Item
                  name="model_name"
                  rules={[{ required: true, message: "请输入模型名" }]}
                  className="w-full !mb-0"
                >
                  <Select
                    optionFilterProp="label"
                    onChange={(_, option) =>
                      handleModelChange(
                        option as {
                          label: string;
                          value: string;
                        }
                      )
                    }
                    options={[
                      { label: "自定义模型", value: "self-defined" },
                      ...modelsOfProvider.map((item) => ({
                        label: item.name,
                        value: item.name,
                      })),
                    ]}
                    showSearch
                    style={{ width: "100%" }}
                  ></Select>
                </Form.Item>
              </div>
            </div>
            {showSelfDefinedModel && (
              <>
                <div className="flex items-center">
                  <label className="w-1/2 text-sm font-medium text-gray-700">
                    {"自定义模型"}
                  </label>
                  <div className="w-1/2 flex items-center">
                    <Form.Item
                      name="self_defined_model"
                      rules={[{ required: true, message: "请输入自定义模型" }]}
                      className="w-full !mb-0"
                    >
                      <Input placeholder="请输入自定义模型" />
                    </Form.Item>
                  </div>
                </div>
              </>
            )}

            <div className="flex items-center">
              <label className="w-1/2 text-sm font-medium text-gray-700">
                {"模型显示名"}
              </label>
              <div className="w-1/2 flex items-center">
                <Form.Item
                  name="name"
                  rules={[{ required: true, message: "请输入模型显示名" }]}
                  className="w-full !mb-0"
                >
                  <Input placeholder="GPT4o Mini" />
                </Form.Item>
              </div>
            </div>

            <div className="flex items-center">
              <label className="w-1/2 text-sm font-medium text-gray-700">
                {t.setting.api_endpoint}
              </label>
              <div className="w-1/2 flex items-center">
                <Form.Item
                  name="base_url"
                  rules={[{ required: true, message: "请输入API端点" }]}
                  className="w-full !mb-0"
                >
                  <Input
                    // onChange={(e) =>
                    //   saveOneSettingToLocal("baseUrl", e.target.value)
                    // }
                    placeholder="https://api.openai.com/"
                    // value={settings.baseUrl}
                  />
                </Form.Item>
              </div>
            </div>

            <div className="flex items-center">
              <label className="w-1/2 text-sm font-medium text-gray-700">
                {t.setting.api_key}
              </label>
              <div className="w-1/2 flex items-center">
                <Form.Item
                  name="api_key"
                  rules={[{ required: true, message: "请输入API密钥" }]}
                  className="w-full !mb-0"
                >
                  <Input
                    type="text"
                    // value={settings.APIKey}
                    // onChange={(e) =>
                    //   saveOneSettingToLocal("APIKey", e.target.value)
                    // }
                    placeholder="sk-xxx"
                  />
                </Form.Item>
              </div>
            </div>
            <div className="flex justify-end space-x-2">
              <Button
                type="default"
                loading={loading}
                onClick={handleTestModel}
              >
                测试
              </Button>
              <Button type="primary" htmlType="submit" loading={loading}>
                添加
              </Button>
            </div>
          </Form>
        </div>
      </Spin>
    </div>
  );
}
