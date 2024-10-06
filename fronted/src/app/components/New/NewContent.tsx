"use client";
import React, { useRef, useEffect, useState } from "react";
import { IconProvider } from "@/app/components/IconProvider";
import { useRouter } from "next/navigation";
import {
  ArrowRightOutlined,
  ArrowUpOutlined,
  CommentOutlined,
  LinkOutlined,
  UpOutlined,
} from "@ant-design/icons";
import { v4 as uuid } from "uuid";

import DropdownMenu from "@/app/components/DropDown";
import HintText from "@/app/components/HintText";
import { Empty, App, Modal, Checkbox, Divider } from "antd";
import Link from "next/link";
import {
  useUserStore,
  useSettingStore,
  useSessionStore,
} from "@/app/lib/store";
import { getUserInfo, refreshToken } from "@/app/http/api";
import { CheckboxChangeEvent } from "antd/es/checkbox";

const plainOptions = [
  "用户信息表",
  "订单记录表",
  "产品目录表",
  "库存管理表",
  "客户反馈表",
  "员工档案表",
  "销售报表",
  "供应商信息表",
  "财务流水表",
  "市场营销表",
];

export default function NewContent({ t }: { t: Global.Dictionary }) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const dropZoneRef = useRef<HTMLDivElement>(null);
  const { message } = App.useApp();

  const [content, setContent] = useState("");
  const [fileList, setFileList] = useState<File[]>([]);
  const [fileUrlList, setFileUrlList] = useState<New.FileItem[]>([]);
  const [showRecents, setShowRecents] = useState(true);
  const [isSelectOpen, setIsSelectOpen] = useState(false);
  const [selectedList, setSelectedList] = useState<string[]>(plainOptions);

  const router = useRouter();
  const { settings, saveOneSettingToLocal } = useSettingStore();
  const { user, setUser } = useUserStore();
  const { chatData, addSession, addMessage, setCurMsg } = useSessionStore();

  const checkAllTbale = plainOptions.length === selectedList.length;
  const indeterminate =
    selectedList.length > 0 && selectedList.length < plainOptions.length;

  const adjustHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      if (textarea.scrollHeight <= 360) {
        textarea.style.height = `${textarea.scrollHeight}px`;
        textarea.style.overflowY = "hidden";
      } else {
        textarea.style.height = "360px";
        textarea.style.overflowY = "auto";
      }
    }
  };

  useEffect(() => {
    adjustHeight();
    if (localStorage.getItem("token") && localStorage.getItem("token") !== "") {
      getUserInfo().then(({ data }) => {
        if (data.code === 200) {
          setUser({
            id: data.data.user_id,
            email: data.data.username,
            name: data.data.nickname,
          });
          refreshToken().then(({ data }) => {
            localStorage.setItem("token", data.data);
          });
        }
      });
    } else {
      router.push("/login");
    }
  }, [content]);

  const isImg = (filename: string) => {
    const imgExt = ["png", "jpg", "jpeg", "gif", "bmp", "webp"];
    const fileExt = filename.split(".").pop();
    return fileExt && imgExt.includes(fileExt);
  };

  const sendMessageAction = () => {
    if (content.trim() == "") {
      return;
    }
    let curMsg = content;

    if (fileList.length != 0) {
      curMsg += fileUrlList
        .map((item) => {
          // 找出图片
          if (isImg(item.filename)) {
            return `![${item.filename}](${item.url})`;
          } else {
            return `[${item.filename}](${item.url})`;
          }
        })
        .join("\n");
    }
    const curSessionId = uuid();
    addSession(curSessionId, curMsg.slice(0, 50));
    addMessage(curSessionId, {
      role: "user",
      content: curMsg,
      id: uuid(),
      createdAt: Date.now(),
    });
    setContent("");
    setFileList([]);
    setFileUrlList([]);
    setCurMsg(curMsg);
    router.push(`/chat/${curSessionId}`);
  };

  const sendMessage = (
    e: React.KeyboardEvent | React.MouseEvent<HTMLDivElement>
  ) => {
    if (
      e.type === "keydown" &&
      (e as React.KeyboardEvent).key === "Enter" &&
      !(e as React.KeyboardEvent).shiftKey
    ) {
      e.preventDefault();
      sendMessageAction();
      // 在这里添加发送消息的逻辑
    } else if (e.type === "click") {
      sendMessageAction();
      // 在这里添加发送消息的逻辑
    }
  };

  const chooseModel = (item: Store.Model) => {
    saveOneSettingToLocal("currentModel", item.value);
    saveOneSettingToLocal("currentDisplayModel", item.label);
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
  };

  const onSelectTable = (list: string[]) => {
    setSelectedList(list);
  };

  const onCheckAllTableChange = (e: CheckboxChangeEvent) => {
    setSelectedList(e.target.checked ? plainOptions : []);
  };

  return (
    <>
      <div
        className={`relative mx-auto h-full w-full max-w-3xl flex-1 l md:px-2 px-4 pb-20 md:pl-8 lg:mt-6 min-h-screen-w-scroll !mt-0 flex flex-col items-center gap-8 pt-12 md:pr-14 2xl:pr-20 `}
      >
        {/* 使用免费计划 */}
        <div className="text-sm text-gray-500 p-2 rounded-full bg-orange-200/50 border border-orange-300">
          {t.new.using}
          <span className="text-orange-600/80 cursor-pointer hover:text-orange-600 hover:underline">
            {t.new.upgrade}
          </span>
        </div>
        {/* 欢迎 */}
        <div className="flex items-center gap-3">
          <div>
            <IconProvider.AI height={32} width={32} fill="#d57858" />
          </div>
          <h1 className="text-[2.5rem] text-gray-800/70 text-center">
            {t.new.welcome} , {user.name}
          </h1>
        </div>
        {/* 输入框 */}
        <div
          ref={dropZoneRef}
          className={`w-full gap-3 flex flex-col shadow-orange-700/30 drop-shadow-xl relative z-10 `}
          onKeyDown={sendMessage}
        >
          <div className="relative p-5 pr-12 bg-white rounded-2xl border border-gray-200">
            <div className="w-full">
              <textarea
                ref={textareaRef}
                value={content}
                onChange={handleChange}
                className="w-full outline-none scrollbar-thin scrollbar-thumb-orange-200 scrollbar-track-transparent resize-none bg-transparent scrollbar"
                placeholder={t.new.placeholder}
                style={{ minHeight: "50px", maxHeight: "360px" }} // 设置一个最小高度
              />
            </div>
            <div className="text-sm relative z-10 flex gap-2">
              <div className="">
                <DropdownMenu
                  items={settings.models}
                  callback={(item) => chooseModel(item)}
                  width="100px"
                >
                  {settings.currentDisplayModel}
                </DropdownMenu>
              </div>
              <div
                className="cursor-pointer h-[30px] flex items-center justify-center px-2 rounded-md border border-gray-300"
                onClick={() => setIsSelectOpen(true)}
              >
                数据选择
              </div>
            </div>
          </div>
          <div
            className="absolute right-2 top-3 bg-orange-700/60 rounded-lg p-2 cursor-pointer hover:bg-orange-700/80 w-8 h-8 flex items-center justify-center text-white"
            onClick={sendMessage}
          >
            <ArrowUpOutlined />
          </div>
          {/* 文件上传 */}
          <div
            className={`relative pt-1  px-2 w-[96%] mx-auto -top-5 bg-orange-200/20 rounded-xl rounded-t-none -z-10 
					border border-orange-300 transition-all duration-300
					${fileList.length == 0 ? "max-h-[3.25rem]" : "max-h-[18rem]"}`}
          >
            <div className=" flex items-center justify-between h-12 select-none">
              <div className="text-sm text-gray-500">
                {fileList.length == 0
                  ? t.new.file_desc
                  : `${fileList.length} ${t.new.file_added}`}
              </div>
              <HintText hintText={t.new.upload_desc}>
                <div
                  className={`text-sm text-gray-500 font-bold cursor-pointer hover:bg-gray-800/10 rounded-lg p-2 flex items-center justify-center
						gap-1`}
                  onClick={() => {
                    message.warning("等待后续开放");
                  }}
                >
                  <LinkOutlined className="text-lg" /> {t.new.upload_file}
                </div>
              </HintText>
            </div>
          </div>
        </div>
        {/* 最近对话 */}
        <div className="w-full">
          <div className="flex justify-between text-sm text-black/80 font-bold">
            <div className="flex items-center gap-2">
              <CommentOutlined className="text-blue-400" /> {t.new.recent_chat}{" "}
              <div
                className={`cursor-pointer hover:bg-gray-800/10 rounded-lg p-1 h-6 flex items-center justify-center scale-90 text-gray-500 z-0`}
                onClick={() => setShowRecents(!showRecents)}
              >
                <UpOutlined
                  className={`transform transition-transform duration-300 ease-in-out select-none  ${
                    showRecents ? "rotate-180" : ""
                  }`}
                />
                {showRecents ? (
                  ""
                ) : (
                  <span className="ml-1 transition-opacity duration-300 ease-in-out">
                    {t.new.expand}
                  </span>
                )}
              </div>
            </div>
            <Link href="/recents">
              <div className="flex items-center gap-1 group cursor-pointer font-medium">
                <span className="group-hover:underline">{t.new.show_all}</span>
                <span className="scale-85">
                  <ArrowRightOutlined className="text-sm" />
                </span>
              </div>
            </Link>
          </div>
          <div
            className={` mt-4 overflow-hidden ${
              chatData.length == 0 ? "h-[200px]" : "grid grid-cols-3 gap-4"
            }`}
          >
            {chatData.length == 0 && (
              <Empty
                description={t.slider.no_history}
                style={{ width: "100%", height: "100%" }}
              />
            )}
            {chatData.length != 0 &&
              chatData.slice(0, 6).map((item, index) => (
                <Link href={`/chat/${item.id}`} key={item.id}>
                  <div
                    key={index}
                    className={`flex flex-col justify-between cursor-pointer p-3 border rounded-md shadow-sm hover:drop-shadow-md
              border-gray-200 bg-gradient-to-b from-white/30 to-white/10 hover:from-white/80 hover:to-white/10 transition-all duration-300 ease-in-out
              ${
                showRecents
                  ? "max-h-[200px] opacity-100"
                  : "max-h-0 opacity-0 overflow-hidden"
              }`}
                  >
                    <div className="">
                      <CommentOutlined />
                    </div>
                    <div className="mt-2 text-sm font-medium truncate">
                      {item.title}
                    </div>
                    <div className="mt-2 text-xs text-gray-500">
                      {new Date(item.createdAt).toLocaleString()}
                    </div>
                  </div>
                </Link>
              ))}
          </div>
        </div>
      </div>
      <Modal
        open={isSelectOpen}
        onCancel={() => setIsSelectOpen(false)}
        onOk={() => setIsSelectOpen(false)}
        okText={t.confirm.yes}
        cancelText={t.confirm.no}
        closable={false}
        centered
        
      >
        <Checkbox
          indeterminate={indeterminate}
          onChange={onCheckAllTableChange}
          checked={checkAllTbale}
        >
          全选
        </Checkbox>
        <Divider />
        <Checkbox.Group
          options={plainOptions}
          value={selectedList}
          onChange={onSelectTable}
        />
      </Modal>
    </>
  );
}
