import React from "react";
import "../globals.css";
import { AntdRegistry } from "@ant-design/nextjs-registry";
import { ConfigProvider, App, ThemeConfig } from "antd";
import SlideServer from "../components/SliderBar/SlideServer";

import { getDictionary } from "@/app/[lang]/i18n";

const config: { theme: ThemeConfig } = {
  theme: {
    token: {
      colorPrimaryBorderHover: "#edc17e",
      colorPrimary: "#bc9c6a",
      colorLinkHover: "inherit",
      colorLinkActive: "inherit",
      colorLink: "inherit",
    },
    components: {
      Slider: {
        trackBg: "#dcb272",
        handleActiveColor: "#edc17e",
        trackHoverBg: "#a8916d",
        handleActiveOutlineColor: "rgba(247, 230, 203, 0.1)",
        handleColor: "#edc17e",
        dotActiveBorderColor: "rgba(247, 230, 203, 0.1)",
      },
    },
  },
};

export default async function I18nLayout({
  children,
  params: { lang },
}: Readonly<{
  children: React.ReactNode;
  params: { lang: Global.SupportedLang };
}>) {
  const t = await getDictionary(lang);

  return (
    <html lang={lang}>
      <head>
        <title>{t.title}</title>
        <meta property="og:title" content={t.title} key="title" />
      </head>

      <body className="h-screen globle-bg transition-all duration-200">
        <AntdRegistry>
          <ConfigProvider theme={config.theme}>
            <App>
              <div className="flex flex-row">
                <SlideServer lang={lang} />
                <div className="flex-1">{children}</div>
              </div>
            </App>
          </ConfigProvider>
        </AntdRegistry>
      </body>
    </html>
  );
}
