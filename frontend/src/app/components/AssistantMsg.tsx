import React, { useState } from "react";
import MarkdownRenderer from "./MarkdownRenderer";
import HintText from "./HintText";
import { IconProvider } from "./IconProvider";
import { Input, Tag } from "antd";
import {
  ArrowUpOutlined,
  CheckOutlined,
  CopyOutlined,
  EditOutlined,
} from "@ant-design/icons";

export default function AssistantMsg({ content, editable = false }: { content: string | React.ReactNode, editable?: boolean }) {
  const [showMarkdown, setShowMarkdown] = useState(true);
  const [showTools, setShowTools] = useState(false);
  const [copyIcon, setCopyIcon] = useState(<CopyOutlined className="h-5" />);
  const [showEdit, setShowEdit] = useState(false);
  const [innerContent, setInnerContent] = useState(content);

  const toolsList = [
    {
      name: "修改",
      icon: (
        <Tag className="!mr-0 !justify-center !items-center">
          <EditOutlined />
        </Tag>
      ),
      show: editable,
      onClick: () => setShowEdit(!showEdit),
    },
    {
      name: showMarkdown ? "显示原文" : "显示转义",
      icon: (
        <Tag className="!mr-0 !justify-center !items-center">
          <IconProvider.Code width={16} height={20} fill="#666" />
        </Tag>
      ),
      show: true,
      onClick: () => setShowMarkdown(!showMarkdown),
    },
    {
      name: "复制",
      icon: (
        <Tag className="!mr-0 !justify-center !items-center">{copyIcon}</Tag>
      ),
      show: true,
      onClick: async () => {
        navigator.clipboard
          .writeText(typeof innerContent === "string" ? innerContent : "")
          .then(() => {
            setCopyIcon(<CheckOutlined className="h-5" />);
            setTimeout(() => {
              setCopyIcon(<CopyOutlined className="h-5" />);
            }, 1000);
          })
          .catch(() => {});
      },
    },
  ];

  const resendMsg = () => {
    console.log("resendMsg");
    setShowEdit(false);
  };

  return (
    <div className="w-full">
      <div
        className="flex items-start relative"
        onMouseEnter={() => setShowTools(true)}
        onMouseLeave={() => setShowTools(false)}
      >
        <div
          className={`flex flex-col items-start bg-gradient-to-b from-[#f8f7f5] to-[#f6f6f2] rounded-lg  gap-3  relative max-w-full border border-white/50 
          ${showEdit ? "w-full p-1" : "px-3 p-2"} w-full
          `}
        >
          <div className="markdown-content border-slate-400 rounded-lg overflow-hidden break-words text-slate-800 w-full">
            {typeof content === "string" ? (
              showMarkdown ? (
                !showEdit ? (
                <MarkdownRenderer content={innerContent as string} />
              ) : (
                <div className="scrollbar p-1 max-w-full flex flex-col gap-2 relative w-full pr-8">
                  <Input.TextArea
                    className="scrollbar "
                    autoSize={{ minRows: 1, maxRows: 5 }}
                    value={innerContent as string}
                    onChange={(e) => setInnerContent(e.target.value)}
                    // onChange={(e) => setContent(e.target.value)}
                  />
                  <div
                    className="absolute right-1 top-1 bg-orange-700/60 rounded-lg p-2 cursor-pointer hover:bg-orange-700/80 w-6 h-6 flex items-center justify-center text-white"
                    onClick={resendMsg}
                  >
                    <ArrowUpOutlined />
                  </div>
                  </div>
                )
              ) : (
                <pre className="whitespace-pre-wrap">{innerContent}</pre>
              )
            ) : (
              content
            )}
          </div>
          <div
            className={`flex absolute -right-1 -bottom-7 h-30  transition-opacity duration-100
            ${
              showTools
                ? "opacity-100 pointer-events-auto"
                : "opacity-0 pointer-events-none"
            }`}
          >
            {toolsList.filter(tool => tool.show).map((tool) => (
              <HintText hintText={tool.name} more={-60} key={tool.name}>
                <div
                  className="text-sm text-slate-500 hover:text-slate-600 flex items-center justify-center w-8 h-8 cursor-pointer"
                  onClick={tool.onClick}
                >
                  {tool.icon}
                </div>
              </HintText>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
