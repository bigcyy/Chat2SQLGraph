"use client";
import {
  ArrowRightOutlined,
  BlockOutlined,
  CloseOutlined,
  DeleteOutlined,
  DownOutlined,
  EditOutlined,
  GithubOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { Jacques_Francois } from "next/font/google";
import React, { useState, useEffect, useRef } from "react";
import { IconProvider } from "../IconProvider";
import { Button, Form, Input, message, Modal, Table } from "antd";
import Setting from "../settings/Setting";
import OutsideClickHandler from "../OutsideClickHandler";
import {
  useSessionStore,
  useUserStore,
  useSettingStore,
  useDatasourceStore,
} from "@/app/lib/store";
import { Empty } from "antd";
import {
  connectDataSource,
  deleteDataSource,
  getDatasourceList,
  getRemoteTableInfo,
  getTableInfo,
  addTablesPOST,
} from "@/app/http/api";
import Comfirm from "../Comfirm";

const playpen_Sans = Jacques_Francois({
  subsets: ["latin"],
  weight: ["400"],
});

const datasourceTestForm = {
  datasource_name: "金融",
  url: "127.0.0.1",
  port: 4306,
  username: "root",
  password: "maybeyou",
  database_name: "bigdata",
};

export default function Slider({ t }: Slider.SlideProps) {
  const path = usePathname();
  const router = useRouter();

  const [isExpanded, setIsExpanded] = useState(false);
  const [isPinned, setIsPinned] = useState(false);

  const [showUserInfo, setShowUserInfo] = useState(false);
  const [showSetting, setShowSetting] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [comfirmVisible, setComfirmVisible] = useState(false);
  const [curCheckedDatasource, setCurCheckedDatasource] =
    useState<Store.Datasource | null>(null);
  const [showEditDatabaseTable, setShowEditDatabaseTable] = useState(false);
  const [tableData, setTableData] = useState<string[]>([]);
  const [tableLoading, setTableLoading] = useState(false);
  const [selectedTableKeys, setSelectedTableKeys] = useState<string[]>([]);

  const databaseForm = Form.useForm<API.DataSource>()[0];

  const sliderRef = useRef<HTMLDivElement>(null);
  const logoRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLDivElement>(null);
  const navRef = useRef<HTMLDivElement>(null);
  const previousLocalTables = useRef<string[]>([]);

  const { user, getUserAvatarFromLocal } = useUserStore();
  const { getSettingFromLocal } = useSettingStore();
  const { chatData, getSessionFromLocal, getReversedChatData } =
    useSessionStore();
  const {
    datasource,
    setDatasource,
    selectedDatasource,
    setSelectedDatasource,
    setTableInfo
  } = useDatasourceStore();

  const popoverSetting = [
    {
      id: "settings",
      title: t.slider.settings,
      click: () => {
        setShowSetting(true);
      },
    },
    {
      id: "logout",
      title: t.slider.logout,
      click: () => {
        router.push("/login");
      },
    },
  ];

  const tableColumns = [
    {
      title: "表名",
      dataIndex: "table_name",
      key: "table_name",
    }
  ];

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isPinned) return;
      if (screen.width < 768) return;
      if (
        titleRef.current?.contains(e.target as Node) ||
        navRef.current?.contains(e.target as Node)
      ) {
        setIsExpanded(true);
      } else if (
        !sliderRef.current?.contains(e.target as Node) &&
        !logoRef.current?.contains(e.target as Node)
      ) {
        setIsExpanded(false);
      }
    };

    document.addEventListener("mousemove", handleMouseMove);
    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
    };
  }, [isPinned]);

  useEffect(() => {
    const defaultSetting = JSON.parse(
      localStorage.getItem("defaultSetting") || "{}"
    );
    getSessionFromLocal();
    getSettingFromLocal();
    getUserAvatarFromLocal();
    if (defaultSetting.pin) {
      setIsPinned(true);
    } else {
      setIsPinned(false);
    }
    if (defaultSetting.showHistory) {
      setShowHistory(true);
    } else {
      setShowHistory(false);
    }
    if (screen.width < 768) {
      setIsPinned(false);
    }
  }, [path]);

  useEffect(() => {
    getDatasourceList().then(({ data }) => {
      if (data.code == 200) {
        setDatasource(data.data);
        setSelectedDatasource(data.data[0]);
        databaseForm.setFieldsValue(datasourceTestForm);
      } else {
        message.error(data.message);
      }
    });
  }, []);

  const getAllTableDetail = async (datasource_id: number) => {
    setTableLoading(true);
    setShowEditDatabaseTable(true);
    Promise.all([
      getRemoteTableInfo(datasource_id),
      getTableInfo(datasource_id),
    ]).then(([remote, local]) => {
      try {
        const remoteData = remote.data;
        const localData = local.data;
        if (remoteData.code == 200 && localData.code == 200) {
          const remoteTableData = remoteData.data;
          const localTableData = localData.data as Store.TableDetail[];
          setTableData(
            remoteTableData.map((item: string[]) => ({
              key: item[0],
              table_name: item[0],
            }))
          );
          setTableInfo(localTableData);
          previousLocalTables.current = localTableData.map((item) => item.name);
          setSelectedTableKeys(localTableData.map((item) => item.name));
        } else {
          if (remoteData.code != 200) {
            message.error(remoteData.message);
          } else {
            message.error(localData.message);
          }
        }
      } catch (e) {
        console.log(e);
        message.error("获取表数据失败");
      } finally {
        setTableLoading(false);
      }
    });
  };

  const onSubmitDatabase = async (values: API.DataSource) => {
    const { data } = await connectDataSource(values);
    if (data.code == 200) {
      setDatasource([...datasource, data.data]);
      message.success("添加成功，请选择你要加入的表格");
      databaseForm.resetFields();
      if (datasource.length == 0) {
        setSelectedDatasource(data.data);
      }
      setCurCheckedDatasource(data.data);
      await getAllTableDetail(data.data.id);
    } else {
      message.error(data.message);
    }
  };

  const handleShowHistory = () => {
    localStorage.setItem(
      "defaultSetting",
      JSON.stringify({
        pin: isPinned,
        showHistory: !showHistory,
      })
    );
    setShowHistory(!showHistory);
  };

  const handleSpin = () => {
    localStorage.setItem(
      "defaultSetting",
      JSON.stringify({
        pin: !isPinned,
        showHistory: showHistory,
      })
    );
    setIsPinned(!isPinned);
  };

  const deleteDatasource = async () => {
    const { data } = await deleteDataSource(curCheckedDatasource?.id!);
    if (data.code == 200) {
      setDatasource(
        datasource.filter((item) => item.id !== curCheckedDatasource?.id)
      );
      setSelectedDatasource(datasource[0]);
      message.success("删除成功");
    } else {
      message.error(data.message);
    }
    setComfirmVisible(false);
  };

  const addTables = async (addTableKeys: string[]) => {
    const { data } = await addTablesPOST(curCheckedDatasource!.id, {
      table_name_list: addTableKeys,
      model_id: 1,
    });
    if (data.code == 200) {
      message.success("添加成功");
    } else {
      message.error(data.message);
    }
  };

  // const deleteTables = async (deleteTableKeys: string[]) => {}

  const onModifyTable = async () => {
    if (!curCheckedDatasource) {
      message.error("请选择一个数据源");
      return;
    }
    // 添加：selectedTableKeys 有但是 previousLocalTables 没有
    // 删除：previousLocalTables 有但是 selectedTableKeys 没有
    const addTableKeys = selectedTableKeys.filter(
      (item) => !previousLocalTables.current.includes(item)
    );

    const deleteTableKeys = previousLocalTables.current.filter(
      (item) => !selectedTableKeys.includes(item)
    );

    setTableLoading(true);
    if (addTableKeys.length > 0) {
      await addTables(addTableKeys);
    }
    // if (deleteTableKeys.length > 0) {
    //   const { data } = await deleteTables(curCheckedDatasource!.id, {
    //     table_name_list: deleteTableKeys,
    //   });
    // }
    setShowEditDatabaseTable(false);
    setTableLoading(false);
  };

  if (path.includes("/login") || path.includes("/register")) {
    return null;
  }

  return (
    <>
      {/* 当屏幕太小时候显示 */}
      <div
        className={`w-18rem text-xl h-5 fixed top-4 left-5 z-30 transition-none sm:hidden transition-all duration-100
        ${isExpanded || isPinned ? "opacity-0" : "opacity-100"}`}
        onClick={() => {
          setIsExpanded(true);
        }}
      >
        <IconProvider.Drawer width={32} height={24} />
      </div>
      {/* 小屏幕时候的遮罩 */}
      <div
        className={`max-sm:fixed max-sm:inset-0 max-sm:bg-black/50 max-sm:z-20 ${
          isExpanded || isPinned
            ? "max-sm:opacity-100"
            : "max-sm:opacity-0 pointer-events-none"
        }`}
        onClick={() => setIsExpanded(false)}
      ></div>

      <div
        className={`ease-in-out duration-200 relative z-20 transition-all  max-sm:translate-x-0 max-sm:left-0${
          isExpanded || isPinned ? "max-sm:translate-x-0 max-sm:left-0" : ""
        }`}
        style={{ width: isPinned ? "18rem" : "0.1rem" }}
      >
        <nav
          className={`z-20 h-screen max-sm:relative max-sm:inset-0 select-none relative `}
          style={{ width: "4.5rem", height: "calc(100vh - 0.1rem)" }}
          ref={navRef}
        >
          <div
            className={`w-18rem text-xl !opacity-100 fixed z-30 top-3 left-3 flex items-center justify-between ${
              isExpanded ? "max-sm:!flex" : "max-sm:hidden"
            }`}
            style={{ width: "calc(18rem - 1.5rem)" }}
            ref={logoRef}
          >
            <Link href="/" className={`${playpen_Sans.className} font-bold`}>
              <span ref={titleRef}>{t.slider.logo}</span>
            </Link>
            {/* 固定 */}
            <div
              className={`cursor-pointer hover:bg-orange-200 rounded-md p-1 w-6 h-6 text-sm flex items-center justify-center transition-all duration-200 max-sm:hidden ${
                isExpanded || isPinned
                  ? "opacity-100 translate-x-0"
                  : "opacity-0 pointer-events-none -translate-x-full"
              }`}
              onClick={handleSpin}
            >
              <IconProvider.VerticalAlignBottomOutlined
                className={` ${
                  isPinned ? "text-orange-500 rotate-90" : "-rotate-90"
                }`}
              />
            </div>
            <div
              className={`cursor-pointer hover:bg-orange-200 rounded-md p-1 w-6 h-6 text-sm items-center justify-center transition-all duration-200 block sm:hidden ${
                isExpanded || isPinned
                  ? "opacity-100 translate-x-0"
                  : "opacity-0 pointer-events-none -translate-x-full"
              }`}
              onClick={() => setIsExpanded(false)}
            >
              <CloseOutlined />
            </div>
          </div>
          <div
            className={`p-3 pb-1 border relative rounded-lg rounded-l-none border-[#dcb272] bg-gradient-to-r from-orange-100/50
              to-orange-50/10 max-sm:from-orange-50 max-sm:to-amber-50 max-sm:shadow-none max-sm:!mt-0 max-sm:rounded-none max-sm:!h-screen
              shadow-2xl shadow-orange-300 ease-in-out duration-100 flex flex-col justify-start ${
                isExpanded || isPinned
                  ? "translate-x-0 opacity-100"
                  : "-translate-x-full opacity-0"
              } ${
              isPinned ? "rounded-r-none shadow-none border-y-0" : "rounded-lg"
            } z-20 backdrop-blur-md`}
            style={{
              width: "18rem",
              height: isPinned ? "100vh" : "calc(100vh - 0.1rem)",
              marginTop: isPinned ? "0" : "0.1rem",
            }}
            ref={sliderRef}
          >
            {/* 新对话及其以上部分 */}
            <div>
              {/* 这是一个单纯的占位符 */}
              <div
                className={`w-18rem text-xl !opacity-100 pointer-events-none h-5`}
                style={{ width: "18rem" }}
              ></div>
              {/* 新对话区域 */}
              <Link href={"/"}>
                <div
                  className={`mt-5 mb-5 cursor-pointer text-orange-700 hover:bg-amber-800/10 rounded-md p-1 flex items-center`}
                  style={{ fontSize: "1.07rem" }}
                >
                  <IconProvider.ChatAdd
                    width={20}
                    height={20}
                    className="-rotate-90"
                  />
                  <span className="ml-1">{t.slider.new}</span>
                </div>
              </Link>
            </div>
            {/* 从这里开始对话历史到底部 */}
            <div className="flex flex-col gap-2 justify-between flex-1 duration-300 transition-all">
              {/* 这里是数据库信息 */}
              <div className={`${showHistory ? "" : "flex-1"} flex flex-col`}>
                <div
                  className="font-bold mb-3 relative group flex justify-between cursor-pointer"
                  onClick={handleShowHistory}
                >
                  <span>数据源配置</span>
                  <div className="cursor-pointer">
                    <DownOutlined
                      className={`${showHistory ? "rotate-180" : ""}`}
                    />
                  </div>
                </div>
                <div
                  className={`flex flex-col gap-2 overflow-hidden ${
                    showHistory ? "max-h-0" : ""
                  }`}
                >
                  <Form
                    form={databaseForm}
                    onFinish={onSubmitDatabase}
                    layout="vertical"
                    className={`flex flex-col gap-2 overflow-hidden`}
                  >
                    <Form.Item
                      className="!m-0 flex-3"
                      name="datasource_name"
                      rules={[{ required: true, message: "请输入数据库别名" }]}
                    >
                      <Input placeholder="数据库别名（显示名称）" />
                    </Form.Item>
                    <div className="flex w-full gap-1">
                      <Form.Item
                        className="!m-0 flex-3"
                        name="url"
                        rules={[
                          { required: true, message: "请输入数据库地址" },
                        ]}
                      >
                        <Input placeholder="数据库地址" />
                      </Form.Item>
                      <Form.Item
                        className="!m-0 flex-1"
                        name="port"
                        rules={[{ required: true, message: "请输入端口" }]}
                      >
                        <Input placeholder="端口" />
                      </Form.Item>
                    </div>

                    <Form.Item
                      className="!m-0"
                      name="username"
                      rules={[
                        { required: true, message: "请输入数据库用户名" },
                      ]}
                    >
                      <Input placeholder="请输入数据库用户名" />
                    </Form.Item>
                    <Form.Item
                      className="!m-0"
                      name="password"
                      rules={[{ required: true, message: "请输入数据库密码" }]}
                    >
                      <Input placeholder="请输入数据库密码" />
                    </Form.Item>
                    <div className="flex w-full gap-1">
                      <Form.Item
                        className="!m-0 flex-3"
                        name="database_name"
                        rules={[
                          { required: true, message: "请输入数据库名称" },
                        ]}
                      >
                        <Input placeholder="请输入数据库名称" />
                      </Form.Item>
                      <Form.Item className="!m-0 flex-1">
                        <Button type="primary" htmlType="submit" block>
                          添加
                        </Button>
                      </Form.Item>
                    </div>
                  </Form>
                  <div className="mb-3 relative mt-5">
                    <span className="text-gray-950 font-bold">
                      已添加的数据源
                    </span>
                    <div className="overflow-y-auto scrollbar h-full gap-1 flex flex-col">
                      {datasource.map((item) => (
                        <div
                          className="flex text-sm relative group transition-all duration-200"
                          key={item.id}
                        >
                          <div
                            className={`hover:bg-amber-800/10 rounded-md p-1 cursor-pointer flex items-center relative w-full
                            ${
                              selectedDatasource?.id === item.id
                                ? "bg-amber-500/10"
                                : ""
                            }`}
                            onClick={() => setSelectedDatasource(item)}
                          >
                            <BlockOutlined />
                            <span className="text-ellipsis overflow-hidden whitespace-nowrap ml-1 mr-1 flex-1 text-gray-600">
                              {item.datasource_name}
                            </span>
                            <div
                              className={`w-8 h-5 cursor-pointer flex items-center justify-between opacity-0 group-hover:opacity-100
                                 transition-opacity duration-200`}
                            >
                              <div
                                className="hover:text-blue-500"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setCurCheckedDatasource(item);
                                  getAllTableDetail(item.id);
                                }}
                              >
                                <EditOutlined />
                              </div>
                              <div
                                className="hover:text-red-500"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setCurCheckedDatasource(item);
                                  setComfirmVisible(true);
                                }}
                              >
                                <DeleteOutlined />
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              <div className={`${showHistory ? "flex-1" : ""}`}>
                {/* 对话历史 */}
                <div
                  className={`font-bold mb-3 relative group flex justify-between cursor-pointer
                  ${showHistory ? "" : ""}`}
                  onClick={() => setShowHistory(!showHistory)}
                >
                  <span>{t.slider.history}</span>
                  <div className="cursor-pointer">
                    <DownOutlined
                      className={`${showHistory ? "" : "rotate-180"}`}
                    />
                  </div>
                </div>
                <div
                  className={`flex flex-col text-sm overflow-y-auto scrollbar gap-1
                    ${showHistory ? "flex-1" : "max-h-0"}`}
                  // style={{ height: "calc(100vh - 15rem)" }}
                >
                  {chatData.length == 0 && (
                    <div className="flex items-center justify-center h-full">
                      <Empty description={t.slider.no_history} />
                    </div>
                  )}
                  {chatData &&
                    getReversedChatData()
                      .slice(0, 10)
                      .map((item) => {
                        return (
                          <Link href={`/chat/${item.id}`} key={item.id}>
                            <div className="hover:bg-amber-800/10 rounded-md p-1 cursor-pointer flex items-center relative group">
                              <IconProvider.Chat width={20} height={20} />
                              <span className="text-ellipsis overflow-hidden whitespace-nowrap ml-1 mr-1 flex-1">
                                {item.title}
                              </span>
                            </div>
                          </Link>
                        );
                      })}
                  {/* 查看所有 */}
                  {chatData.length > 10 && (
                    <Link href={"/recents"} className="gap-1 mt-3">
                      <div className="flex h-5 font-bold cursor-pointer hover:text-black/70">
                        <span>{t.slider.show_all}</span>
                        <span className="w-5 h-5 text-sm flex items-center justify-center text-gray-500">
                          <ArrowRightOutlined className="scale-90" />
                        </span>
                      </div>
                    </Link>
                  )}
                </div>
              </div>
              {/* 底部区域 */}
              <div className="h-20 flex flex-col justify-between">
                {/* 用户信息 */}
                <div
                  className={`flex items-centergap-2 p-1 pl-2 pr-2 rounded-md h-10
            cursor-pointer border border-gray-300/50 hover:border-gray-300
            bg-gradient-to-b from-orange-50 via-orange-100/70 to-orange-50
            shadow-sm hover:shadow-sm transition-all duration-200 relative`}
                >
                  <div
                    className="flex items-center justify-between gap-2 w-full"
                    onClick={() => setShowUserInfo(!showUserInfo)}
                  >
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center overflow-hidden`}
                    >
                      <Image
                        width={24}
                        height={24}
                        src={user.avatar!}
                        alt={t.slider.avatar}
                        className="object-cover w-full h-full rounded-full"
                      />
                    </div>
                    <div className="h-10 flex-1 leading-10 text-[0.8rem] text-center overflow-hidden text-ellipsis whitespace-nowrap">
                      {user.email}
                    </div>
                    <div className="text-xs flex items-center justify-center scale-75">
                      <DownOutlined />
                    </div>
                  </div>
                  <OutsideClickHandler
                    onOutsideClick={() => setShowUserInfo(false)}
                  >
                    <div
                      className={`absolute left-0 bottom-full w-full transition-all duration-200
                    border rounded-md shadow-sm shadow-gray-500/20 bg-orange-50 overflow-hidden p-1`}
                      style={{
                        maxHeight: showUserInfo ? "500px" : "0",
                        opacity: showUserInfo ? "1" : "0",
                        transform: showUserInfo
                          ? "translateY(0)"
                          : "translateY(100%)",
                        visibility: showUserInfo ? "visible" : "hidden",
                      }}
                    >
                      {popoverSetting.map((item) => {
                        return (
                          <div
                            className="h-6 w-full hover:bg-orange-100 cursor-pointer p-1 flex items-center text-sm"
                            key={item.id}
                            onClick={item.click}
                          >
                            {item.title}
                          </div>
                        );
                      })}
                    </div>
                  </OutsideClickHandler>
                </div>
                {/* 设置 */}
                <div className="p-1 pl-2 pr-2 flex justify-between items-center">
                  <div
                    onClick={() => setShowSetting(true)}
                    className="cursor-pointer rounded-lg hover:bg-orange-200 w-6 h-6 flex items-center justify-center"
                  >
                    <SettingOutlined />
                  </div>
                  <div className="cursor-pointer rounded-lg hover:bg-orange-200 w-6 h-6 flex items-center justify-center">
                    <Link
                      href="https://github.com/1653756334/claude-imitate"
                      target="_blank"
                    >
                      <GithubOutlined />
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div
            className={`w-8 h-16 rounded-full flex flex-col justify-between items-center overflow-hidden absolute bottom-3 left-3 transition-all duration-200 max-sm:hidden ${
              isExpanded || isPinned
                ? "opacity-0 translate-x-2"
                : "opacity-100 translate-x-0"
            }`}
          >
            <div className="border rounded-full overflow-hidden p-1 w-8 h-8">
              <Image
                width={24}
                height={24}
                src={user.avatar!}
                alt={t.slider.avatar}
                className="object-cover w-full h-full rounded-full"
              />
            </div>
            <IconProvider.Drawer />
          </div>
        </nav>
      </div>
      {/* 设置 */}
      <Modal
        open={showSetting}
        onCancel={() => setShowSetting(false)}
        onOk={() => setShowSetting(false)}
        centered
        okText={t.confirm.yes}
        cancelText={t.confirm.no}
        closable={false}
        maskClosable={false}
      >
        <Setting t={t} />
      </Modal>
      {/* 添加数据源过后选表 */}
      <Modal
        open={showEditDatabaseTable}
        onCancel={() => setShowEditDatabaseTable(false)}
        onOk={onModifyTable}
        centered
        okText={"修改"}
        cancelText={t.confirm.no}
        closable={false}
        maskClosable={false}
        title="选择要添加的表"
        confirmLoading={tableLoading}
      >
        <Table
          scroll={{ y: 400 }}
          dataSource={tableData}
          columns={tableColumns}
          rowSelection={{
            onChange: (selectedRowKeys) => {
              setSelectedTableKeys(selectedRowKeys as string[]);
            },
            selectedRowKeys: selectedTableKeys,
          }}
          className="scrollbar"
          bordered
          sticky
          pagination={false}
          loading={tableLoading}
        />
      </Modal>

      <Comfirm
        title={"确定要删除数据源吗？"}
        content={"删除后将无法恢复"}
        onCancel={() => setComfirmVisible(false)}
        onConfirm={deleteDatasource}
        visible={comfirmVisible}
        yesText={t.confirm.yes}
        noText={t.confirm.no}
      />
    </>
  );
}
