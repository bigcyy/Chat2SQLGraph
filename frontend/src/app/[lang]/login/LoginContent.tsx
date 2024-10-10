"use client";
import React, { useEffect, useState } from "react";
import { IconProvider } from "@/app/components/IconProvider";
import PrintWord from "@/app/components/PrintWord";
import { Form, message, Tabs } from "antd";
import {useRouter} from "next/navigation";

import { login, register } from "@/app/http/api";

import Login from "./components/Login";
import Register from "./components/Register";

const wordList = [
  "Useful Easy Powerful",
  "对话 - SQL - 图表",
  "不要局限你的想象力",
];

export default function LoginContent({ t }: Login.LoginContentProps) {
  const [activeTab, setActiveTab] = useState("login");
  const [word, setWord] = useState(wordList[0]);
  const router = useRouter();

  const [form] = Form.useForm<Login.LoginFrom>();
  const [formRegister] = Form.useForm<Login.RegisterFrom>();
  useEffect(() => {
    const interval = setInterval(() => {
      setWord(wordList[Math.floor(Math.random() * wordList.length)]);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const onLogin = async (form: Login.LoginFrom) => {
    const {data} = await login(form);
    if(data.code === 200) {
      localStorage.setItem("token", data.data);
      router.replace("/");
    } else {
      message.error(data.message);
    }
  };

  const onRegister = async (form: Login.RegisterFrom) => {
    const {data} = await register(form);
    if(data.code === 200) {
      message.success("注册成功");
      setActiveTab("login");
    } else {
      message.error(data.message);
    }
  };

  const tableItems = [
    {
      key: "login",
      label: t.login.login,
      children: <Login form={form} onLogin={onLogin} t={t} />,
    },
    {
      key: "register",
      label: t.login.register,
      children: <Register form={formRegister} onRegister={onRegister} t={t} />,
    },
  ];

  return (
    <div className="h-screen bg-[#f5f4ef]">
      <div className="w-1/2 bg-[#f5f4ef] mx-auto max-sm:w-screen">
        <div className="flex grow flex-col justify-center pt-2 [@media(min-height:800px)]:pt-6 [@media(min-height:900px)]:pt-10 w-full min-h-screen px-5 -translate-y-10">
          <div className="flex justify-center gap-3 items-center text-2xl">
            <IconProvider.AI fill="#d97757" width={32} height={32} /> {t.title}
          </div>
          <div className="select-none mt-12">
            <PrintWord word={word} />
          </div>
          <div className=" mt-16 w-[460px] max-sm:w-[90vw] mx-auto bg-[#f1efe7] rounded-3xl border-2 border-[#d2d0c5] px-10 py-6">
            <Tabs
              activeKey={activeTab}
              onChange={setActiveTab}
              items={tableItems}
              defaultActiveKey="login"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
