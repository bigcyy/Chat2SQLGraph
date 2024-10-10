import {
  LockOutlined,
  MailOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { Button, Form, Input } from "antd";
import React from "react";

export default function Register({
  form,
  onRegister,
  t,
}: Login.RegisterProps) {
  return (
    <div>
      <Form name="register" onFinish={onRegister} form={form}>
        <Form.Item
          name="nickname"
          rules={[{ required: true, message: t.login.nickname_required }]}
        >
          <Input prefix={<UserOutlined />} placeholder={t.login.nickname} />
        </Form.Item>
        <Form.Item
          name="username"
          rules={[
            { required: true, message: t.login.username_required },
          ]}
        >
          <Input prefix={<MailOutlined />} placeholder={t.login.username} />
        </Form.Item>
        <Form.Item
          name="password"
          rules={[{ required: true, message: t.login.password_required }]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder={t.login.password}
          />
        </Form.Item>
        <Form.Item
          name="re_password"
          dependencies={["password"]}
          rules={[
            { required: true, message: t.login.confirm_password_required },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue("password") === value) {
                  return Promise.resolve();
                }
                return Promise.reject(
                  new Error(t.login.confirm_password_not_match)
                );
              },
            }),
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder={t.login.confirm_password}
          />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" block>
            {t.login.register}
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
}
