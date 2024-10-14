"use client";
import React, { useRef, useEffect, useState } from "react";
import { IconProvider } from "@/app/components/IconProvider";
import { useRouter } from "next/navigation";
import {
  ArrowRightOutlined,
  ArrowUpOutlined,
  CommentOutlined,
  UpOutlined,
} from "@ant-design/icons";

import DropdownMenu from "@/app/components/DropDown";
import { Empty, App, Modal, Checkbox, Divider, Select, Spin } from "antd";
import Link from "next/link";
import {
  useUserStore,
  useSettingStore,
  useDatasourceStore,
  useChatStore,
} from "@/app/lib/store";
import {
  createSession,
  getTableInfo,
  getUserInfo,
  refreshToken,
} from "@/app/http/api";
import { CheckboxChangeEvent } from "antd/es/checkbox";

export default function NewContent({ t }: { t: Global.Dictionary }) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const dropZoneRef = useRef<HTMLDivElement>(null);
  const { message } = App.useApp();

  const [content, setContent] = useState("");
  const [showRecents, setShowRecents] = useState(true);
  const [isSelectOpen, setIsSelectOpen] = useState(false);
  const [tableLoading, setTableLoading] = useState(false);

  const router = useRouter();
  const { settings, setCurrentModelId } = useSettingStore();
  const { user } = useUserStore();
  const { setCurMsg, chatHistory, setChatHistory } = useChatStore();
  const {
    datasource,
    selectedDatasource,
    setSelectedDatasource,
    tableInfo,
    setTableInfo,
    setSelectedTableKeys,
    selectedTableKeys,
  } = useDatasourceStore();


  const checkAllTbale = tableInfo.length === selectedTableKeys.length;
  const indeterminate =
    selectedTableKeys.length > 0 && selectedTableKeys.length < tableInfo.length;

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
  }, [content]);

  const sendMessageAction = async () => {
    // if (selectedTableKeys.length == 0) {
    //   message.warning("请选择数据表");
    //   onSelectDatasource();
    //   return;
    // }
    if (content.trim() == "") {
      return;
    }
    const res = await createSession(selectedDatasource!.id!);
    const session_id = res.data.data;
    setCurMsg(content);
    setChatHistory([{
      id: session_id,
      datasource_id: selectedDatasource!.id!,
      user_demand: content,
        created_at: Date.now(),
      },
      ...chatHistory,
    ]);
    router.push(`/chat/${selectedDatasource!.id}/${session_id}`);
  };

  const sendMessage = async (
    e: React.KeyboardEvent | React.MouseEvent<HTMLDivElement>
  ) => {
    if (
      e.type === "keydown" &&
      (e as React.KeyboardEvent).key === "Enter" &&
      !(e as React.KeyboardEvent).shiftKey
    ) {
      e.preventDefault();
      sendMessageAction();
    } else if (e.type === "click") {
      await sendMessageAction();
    }
  };

  // const chooseModel = (item: Store.Model) => {
  //   saveOneSettingToLocal("currentModel", item.value);
  //   saveOneSettingToLocal("currentDisplayModel", item.label);
  // };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
  };

  const onSelectTable = (list: string[]) => {
    setSelectedTableKeys(list);
  };

  const onCheckAllTableChange = (e: CheckboxChangeEvent) => {
    setSelectedTableKeys(
      e.target.checked ? tableInfo.map((item) => item.id?.toString()) : []
    );
  };

  const handleChangeDatasource = (value: string) => {
    setTableLoading(true);
    getTableInfo(parseInt(value)).then(({ data }) => {
      if (data.code == 200) {
        const tablleData = data.data as Store.TableDetail[];
        setTableInfo(tablleData);
        setTableLoading(false);
        setSelectedTableKeys([]);
        setSelectedDatasource(
          datasource.find((item) => item.id?.toString() === value)!
        );
      } else {
        setTableLoading(false);
        message.error(data.message);
      }
    });
  };

  const onSelectDatasource = () => {
    if (datasource.length == 0) {
      message.warning("请先在左侧侧边栏添加数据源");
      return;
    }
    if (!selectedDatasource) {
      setSelectedDatasource(datasource[0]);
    }
    setIsSelectOpen(true);
    setTableLoading(true);
    getTableInfo(selectedDatasource ? selectedDatasource!.id! : datasource[0].id!).then(({ data }) => {
      if (data.code == 200) {
        const tablleData = data.data as Store.TableDetail[];
        setTableInfo(tablleData);
        setTableLoading(false);
      } else {
        setTableLoading(false);
        message.error(data.message);
      }
    });
  };

  return (
    <>
      <div
        className={`relative mx-auto h-full w-full max-w-3xl flex-1 l md:px-2 px-4 pb-20 md:pl-8 lg:mt-6 min-h-screen-w-scroll !mt-0 flex flex-col items-center gap-8 pt-12 md:pr-14 2xl:pr-20 `}
      >
        {/* 使用免费计划 */}
        <div className="text-sm text-gray-500 p-2 rounded-full bg-orange-200/50 border border-orange-300">
          您正在使用测试版本
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
                  items={settings.models.map((item) => ({
                    label: item.name,
                    value: item.id.toString(),
                  }))}
                  callback={(item) => {setCurrentModelId(parseInt(item.value))}}
                  width="100px"
                >
                  {settings.models.find(item => item.id === settings.currentModelId)?.name}
                </DropdownMenu>
              </div>
              <div
                className="cursor-pointer h-[30px] flex items-center justify-center px-2 rounded-md border border-gray-300"
                onClick={onSelectDatasource}
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
          {/* 这里要改 */}
          <div
            className={` mt-4 overflow-hidden ${
              chatHistory.length == 0 ? "h-[200px]" : "grid grid-cols-3 gap-4"
            }`}
          >
            {chatHistory.length == 0 && (
              <Empty
                description={t.slider.no_history}
                style={{ width: "100%", height: "100%" }}
              />
            )}
            {chatHistory.length != 0 &&
              chatHistory.slice(0, 6).map((item, index: number) => (
                <Link href={`/chat/${item.datasource_id}/${item.id}`} key={item.id}>
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
                      {item.user_demand}
                    </div>
                    <div className="mt-2 text-xs text-gray-500">
                      {new Date(item.created_at).toLocaleString()}
                    </div>
                  </div>
                </Link>
              ))}
          </div>
        </div>
      </div>
      <Modal
        title="数据选择"
        open={isSelectOpen}
        onCancel={() => setIsSelectOpen(false)}
        onOk={() => setIsSelectOpen(false)}
        okText={t.confirm.yes}
        cancelText={t.confirm.no}
        closable={false}
        maskClosable={false}
        centered
      >
        <div>
          <div className="flex items-center gap-2">
            <div className="">数据源选择：</div>
            <Select
              options={datasource.map((item) => ({
                value: item.id?.toString(),
                label: item.datasource_name,
              }))}
              value={selectedDatasource?.id?.toString()}
              onChange={handleChangeDatasource}
              className="w-1/2"
            />
          </div>
          <Divider />
          <Checkbox
            indeterminate={indeterminate}
            onChange={onCheckAllTableChange}
            checked={checkAllTbale}
          >
            全选
          </Checkbox>
          <Divider />
          <Spin spinning={tableLoading} tip="加载中...">
            <Checkbox.Group
              options={
                tableInfo.length > 0
                  ? tableInfo.map((item) => ({
                      value: item.id?.toString(),
                      label: item.name,
                    }))
                  : []
              }
              value={selectedTableKeys}
              onChange={onSelectTable}
            />
          </Spin>
        </div>
      </Modal>
    </>
  );
}
