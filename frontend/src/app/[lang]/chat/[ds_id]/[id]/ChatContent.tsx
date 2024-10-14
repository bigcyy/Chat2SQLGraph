"use client";
import { CommentOutlined, DownOutlined } from "@ant-design/icons";
import React, { useRef, useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

import OutsideClickHandler from "@/app/components/OutsideClickHandler";
import Confirm from "@/app/components/Comfirm";
import Modify from "@/app/components/Modify";
import SelfMessage from "@/app/components/SelfMessage";
import AssistantMsg from "@/app/components/AssistantMsg";
import {
  useUserStore,
  useChatStore,
  useDatasourceStore,
  useSettingStore,
} from "@/app/lib/store";
import { throttle } from "@/app/lib/utils";
import { message as Message, Table } from "antd";
import { IconProvider } from "@/app/components/IconProvider";
import { getCurrentChat, chat } from "@/app/http/api";
import Chart from "@/app/components/Chart";
export default function ChatContent({ t }: Chat.ChatContentProps) {
  const pathname = usePathname();
  const session_id = pathname.split("/").slice(-1)[0];
  const datasource_id = pathname.split("/").slice(-2)[0];

  const [showModify, setShowModify] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [content, setContent] = useState("");
  const [chatList, setChatList] = useState<Global.ChatItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [title, setTitle] = useState("");
  const breakStreamRef = useRef(false);

  const chatListRef = useRef<HTMLDivElement>(null);
  const { user } = useUserStore();

  const { curMsg, setCurMsg } = useChatStore();
  const { selectedTableKeys, setSelectedDatasource, datasource } =
    useDatasourceStore();
  const { settings } = useSettingStore();

  const router = useRouter();

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 370)}px`;
    }
  };

  const [confirmData, setConfirmData] = useState<Comfirm.ComfirmProps>({
    title: "",
    content: "",
    onCancel: () => {},
    onConfirm: () => {},
    visible: false,
    yesText: "",
    noText: "",
  });
  const [modifyData, setModifyData] = useState<Modify.ModifyProps>({
    title: "",
    content: "",
    onCancel: () => {},
    onConfirm: () => {},
    visible: false,
    yesText: "",
    noText: "",
  });

  const hasSentMessage = useRef(true);

  const LoadHistory = () => {
    getCurrentChat(datasource_id, session_id)
      .then(({ data }: any) => {
        if (data.code === 200) {
          setChatList([
            {
              role: "user",
              content: data.data.user_demand,
              createdAt: data.data.created_at,
            },
          ]);
          setTitle(data.data.user_demand.slice(0, 50));
          setSelectedDatasource(
            datasource.find((item) => item.id.toString() == datasource_id)!
          );
          const sse_message_list = data.data.sse_message_list;
          sse_message_list.forEach((item: any) => {
            setResultChatItem(JSON.parse(item).data);
          });
        } else {
          Message.error("获取历史记录失败");
          router.push("/");
        }
      })
      .catch((err: any) => {
        console.log(err);
        Message.error("获取历史记录失败");
        router.push("/");
      });
  };

  useEffect(() => {
    // 说明从上个页面过来，需要发送
    if (curMsg !== "" && hasSentMessage.current) {
      streamChat();
      setTitle(curMsg.slice(0, 50));
      // 标记消息已发送
      hasSentMessage.current = false;
      setChatList([
        ...chatList,
        {
          role: "user",
          content: curMsg,
          createdAt: Date.now(),
        },
      ]);
      // 清除 curMsg，防止重复发送
      setCurMsg("");
    } else if (hasSentMessage.current) {
      // 说明是历史记录
      LoadHistory();
      hasSentMessage.current = false;
    }
    // 清理函数
    return () => {
      hasSentMessage.current = false;
    };
  }, []);

  // useEffect(() => {
  //   setChatList(session.messages);
  // }, [session.messages.length]);

  useEffect(() => {
    adjustTextareaHeight();
  }, [content]);

  const onDeleteChat = () => {
    const data = {
      title: t.chat.delete_title,
      content: t.chat.delete_content,
      yesText: t.confirm.delete,
      noText: t.confirm.no,
      visible: true,
    };
    setConfirmData({
      ...data,
      onConfirm: () => {
        setConfirmData({ ...data, visible: false });
        // deleteSession(session_id);
        router.push("/new");
      },
      onCancel: () => {
        setConfirmData({ ...data, visible: false });
      },
    });
  };

  const onRenameChat = () => {
    const data = {
      title: t.chat.rename_title,
      content: title,
      yesText: t.confirm.rename,
      noText: t.confirm.no,
      visible: true,
    };
    setModifyData({
      ...data,
      onConfirm: (value: string) => {
        // renameSession(session_id, value);
        setModifyData({ ...data, visible: false, content: value });
      },
      onCancel: () => {
        setModifyData({ ...data, visible: false });
      },
    });
  };

  const isScrolledToBottom = () => {
    if (chatListRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = chatListRef.current;
      return scrollTop + clientHeight >= scrollHeight - 30; // 允许30px的误差
    }
    return false;
  };

  const downToBottom = () => {
    if (chatListRef.current) {
      setTimeout(() => {
        chatListRef.current?.scrollTo({
          top: chatListRef.current.scrollHeight + 100,
          behavior: "smooth",
        });
      }, 100);
    }
  };

  const throttleDownToBottom = throttle(downToBottom, 50);

  const checkIsJson = (str: string) => {
    try {
      JSON.parse(str);
      return true;
    } catch (e) {
      return false;
    }
  };

  const setResultChatItem = (content: string) => {
    if (checkIsJson(content)) {
      const parsed = JSON.parse(content);
      if (parsed.table_ids) {
        const item = {
          role: "assistant" as const,
          content: `**选择表**：${parsed.table_ids.join(",")}\n\n**原因**：${
            parsed.reason
          }`,
          createdAt: Date.now(),
        };
        setChatList((prev) => [...prev, item]);
      } else if (parsed.sql || parsed.sql == "") {
        const item = {
          role: "assistant" as const,
          content: `**生成SQL**：${parsed.sql}\n\n**原因**：${parsed.think}`,
          createdAt: Date.now(),
          editable: true,
        };
        setChatList((prev) => [...prev, item]);
      } else if (parsed.columns) {
        // 表格数据
        const columns = parsed.columns.map((item: string) => ({
          title: item,
          dataIndex: item,
          key: item,
          defaultSortOrder: "ascend",
          sorter: (a: any, b: any) => a[item] - b[item],
        }));
        const showData = parsed.data.slice(0, 100);
        const data = showData.map((item: any[], index: number) => {
          let everyItem: Record<string, any> = {};
          item.forEach((val: any, i: number) => {
            everyItem[columns[i].dataIndex] = val;
          });
          everyItem.key = index;
          return everyItem;
        });
        let moreHint = "";
        if (parsed.data.length > 100) {
          moreHint = `表格仅展示前100条数据，共${parsed.data.length}条`;
        }
        const item = {
          role: "assistant" as const,
          content: (
            <div>
              <Table columns={columns} dataSource={data} scroll={{ x: true }} />
              {moreHint}
            </div>
          ),
          createdAt: Date.now(),
        };
        setChatList((prev) => [...prev, item]);
      } else if (parsed.series) {
        const item = {
          role: "assistant" as const,
          content: <Chart option={parsed} />,
          createdAt: Date.now(),
        };
        setChatList((prev) => [...prev, item]);
      }
    } else {
      const item = {
        role: "assistant" as const,
        content,
        createdAt: Date.now(),
      };
      setChatList((prev) => [...prev, item]);
    }
  };

  async function streamChat() {
    setLoading(true);
    breakStreamRef.current = false;
    const response = await chat(datasource_id, session_id, {
      user_select_tables: selectedTableKeys,
      user_demand: curMsg,
      model_id: settings.currentModelId,
    });

    if (!response.ok) {
      const res = await response.json();
      let errMsg = JSON.stringify(res);
      console.log(errMsg);
      Message.error("发送信息失败");
      downToBottom();
      setLoading(false);
      return;
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader!.read();

      if (done) {
        setLoading(false);
        break;
      }

      const chunk = decoder.decode(value);
      const lines = chunk.split("\n");

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6);
          if (data === "[DONE]") {
            downToBottom();
            setLoading(false);
          } else {
            try {
              const parsed = JSON.parse(data);
              const content = parsed.data;
              if (content) {
                try {
                  setResultChatItem(content);
                } catch (error) {
                  console.error("解析出错:", error);
                }
              }
              // 如果内容滑到了底部，就一直往底下滚动
              if (isScrolledToBottom()) {
                throttleDownToBottom();
              }
            } catch (error) {
              console.error("解析JSON时出错:", error);
            }
          }
        }
      }
    }
  }

  // const sendMessage = async () => {
  //   if (content.trim() === "") {
  //     return;
  //   }
  //   const randonId = uuid();
  //   downToBottom();
  //   const message = {
  //     role: "user" as const,
  //     content,
  //     id: randonId,
  //     createdAt: Date.now(),
  //   };
  //   addMessage(session_id, message);
  //   setContent("");
  //   streamChat(message);
  // };

  return (
    <div>
      <header className=" top-0 z-10 -mb-6 flex h-14 items-center gap-3 pl-11 pr-2 md:pb-0.5 md:pl-6 relative w-[80%] mx-auto">
        <div className=" pointer-events-none absolute inset-0 -bottom-7 z-[-1] bg-gradient-to-t from-transparent via-amber-900/5 to-amber-900/10 blur"></div>
        <div className="flex items-center gap-2 mx-auto text-lg text-black/80">
          <div>
            <CommentOutlined />
          </div>
          <OutsideClickHandler onOutsideClick={() => setShowModify(false)}>
            <div
              className="py-1 px-2 flex items-center gap-1 cursor-pointer rounded-lg hover:bg-amber-900/10 relative "
              onClick={() => setShowModify(!showModify)}
            >
              <div className="max-w-3xl overflow-hidden whitespace-nowrap text-ellipsis">
                {title}
              </div>
              <DownOutlined className="text-sm" />
              <div
                className={`absolute whitespace-nowrap top-full left-1/2 -translate-x-1/2 translate-y-1 bg-[#e2dbca] flex flex-col items-center border border-amber-600/50 rounded-lg justify-center gap-1 p-1 text-sm
                ${
                  showModify ? "opacity-100" : "opacity-0 pointer-events-none"
                }`}
              >
                <div
                  className="cursor-pointer px-2 w-full text-center hover:bg-amber-900/10 rounded-md"
                  onClick={onRenameChat}
                >
                  {t.chat.rename}
                </div>
                <div
                  className="cursor-pointer px-2 w-full text-center hover:bg-amber-900/10 rounded-md"
                  onClick={onDeleteChat}
                >
                  {t.chat.delete}
                </div>
              </div>
            </div>
          </OutsideClickHandler>
        </div>
      </header>
      <main className="flex-1 flex flex-col px-4 mx-auto w-full pt-1 h-[calc(100vh-3.3rem)] mt-5 max-md:max-w-[100vw] max-md:px-3">
        {/* 聊天记录 */}
        <div
          className="flex-1 overflow-y-auto scrollbar flex w-full box-border px-2 max-md:px-0 my-5"
          ref={chatListRef}
        >
          <div className="max-w-3xl mx-auto flex flex-col gap-5 items-start w-full max-md:px-5">
            {chatList.map((item, index) => {
              if (item.role === "user") {
                return (
                  <SelfMessage
                    key={"user" + index}
                    content={item.content as string}
                    avatar={user.avatar!}
                    onReEdit={() => {
                      setContent(item.content as string);
                    }}
                  />
                );
              } else {
                return (
                  <AssistantMsg
                    key={"assistant" + index}
                    content={item.content}
                    editable={item.editable}
                  />
                );
              }
            })}
            {/* {curChat && curChat.trim() !== "" && (
              <AssistantMsg content={curChat} />
            )} */}
            <div
              style={{ animation: loading ? "spin 1s linear infinite" : "" }}
            >
              <IconProvider.LoadingTag fill="#da8d6d" width={28} height={28} />
            </div>
          </div>
        </div>
      </main>
      <Confirm {...confirmData} />
      <Modify {...modifyData} />
    </div>
  );
}
