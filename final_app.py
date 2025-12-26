import streamlit as st
import pandas as pd
import plotly.express as px


def get_dataframe_from_excel():
    # 读取Excel文件数据
    df = pd.read_excel(
        'supermarket_sales.xlsx',
        sheet_name="销售数据",
        skiprows=1,  # 跳过第1行（标题行）
        index_col="订单号"
    )
    # 处理“时间”列，转换为datetime并提取小时
    df["小时数"] = pd.to_datetime(df["时间"], format="%H:%M:%S").dt.hour
    return df


def add_sidebar_func(df):
    # 构建侧边栏
    with st.sidebar:
        st.subheader("请筛选数据：")

        # 城市筛选
        city_unique = df["城市"].unique()
        city = st.multiselect(
            "请选择城市：",
            options=city_unique,
            default=city_unique
        )

        # 顾客类型筛选
        customer_type_unique = df["顾客类型"].unique()
        customer_type = st.multiselect(
            "请选择顾客类型：",
            options=customer_type_unique,
            default=customer_type_unique
        )

        # 性别筛选
        gender_unique = df["性别"].unique()
        gender = st.multiselect(
            "请选择性别：",
            options=gender_unique,
            default=gender_unique
        )

        # 筛选数据
        df_selection = df.query(
            "城市 == @city & 顾客类型 == @customer_type & 性别 == @gender"
        )
        return df_selection


def product_line_chart(df):
    # 按“产品类型”分组计算总销售额
    sales_by_product_line = df.groupby(by=["产品类型"])[["总价"]].sum().sort_values(by="总价")
    # 生成条形图
    fig_product_sales = px.bar(
        sales_by_product_line,
        x="总价",
        y=sales_by_product_line.index,
        orientation="h",
        title="<b>按产品类型划分的销售额</b>"
    )
    return fig_product_sales


def hour_chart(df):
    # 按“小时数”分组计算总销售额
    sales_by_hour = df.groupby(by=["小时数"])[["总价"]].sum()
    # 生成条形图
    fig_hour_sales = px.bar(
        sales_by_hour,
        x=sales_by_hour.index,
        y="总价",
        title="<b>按小时数划分的销售额</b>"
    )
    return fig_hour_sales


def main_page_demo(df):
    # 设置页面标题
    st.title("销售仪表板")
    # 构建信息区（3个容器）
    left_key_col, middle_key_col, right_key_col = st.columns(3)

    # 计算关键指标
    total_sales = int(df["总价"].sum())
    average_rating = round(df["评分"].mean(), 1)
    star_rating_string = ":star:" * int(round(average_rating, 0))
    average_sale_by_transaction = round(df["总价"].mean(), 2)

    # 左侧：总销售额
    with left_key_col:
        st.subheader("总销售额：")
        st.subheader(f"RMB ¥ {total_sales:,}")

    # 中间：顾客评分平均值
    with middle_key_col:
        st.subheader("顾客评分的平均值：")
        st.subheader(f"{average_rating} {star_rating_string}")

    # 右侧：每单平均销售额
    with right_key_col:
        st.subheader("每单的平均销售额：")
        st.subheader(f"RMB ¥ {average_sale_by_transaction}")

    # 分割线
    st.divider()

    # 构建图表区（2个容器）
    left_chart_col, right_chart_col = st.columns(2)

    # 左侧：小时销售额图表
    with left_chart_col:
        hour_fig = hour_chart(df)
        st.plotly_chart(hour_fig, use_container_width=True)

    # 右侧：产品类型销售额图表
    with right_chart_col:
        product_fig = product_line_chart(df)
        st.plotly_chart(product_fig, use_container_width=True)


def run_app():
    # 设置页面配置
    st.set_page_config(
        page_title="销售仪表板",
        page_icon="📊",
        layout="wide"
    )
    # 获取数据
    sale_df = get_dataframe_from_excel()
    # 侧边栏筛选
    df_selection = add_sidebar_func(sale_df)
    # 渲染主页面
    main_page_demo(df_selection)


if __name__ == "__main__":
    run_app()
