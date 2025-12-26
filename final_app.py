import streamlit as st
import pandas as pd
import plotly.express as px


def get_dataframe_from_excel():
    # 读取Excel文件数据（兼容无Excel文件的情况，增加异常处理）
    try:
        df = pd.read_excel(
            'supermarket_sales.xlsx',
            sheet_name="销售数据",
            skiprows=1,  # 跳过第1行（标题行）
            index_col="订单号",
            engine='openpyxl'  # 显式指定引擎，避免依赖问题
        )
    except FileNotFoundError:
        # 无Excel文件时生成模拟数据，方便你测试
        st.warning("未找到supermarket_sales.xlsx，使用模拟数据演示！")
        data = {
            "订单号": [1001, 1002, 1003, 1004, 1005, 1006],
            "时间": ["09:30:00", "10:15:00", "11:20:00", "14:40:00", "15:10:00", "16:30:00"],
            "城市": ["上海", "北京", "上海", "广州", "北京", "广州"],
            "顾客类型": ["会员", "普通", "会员", "普通", "会员", "普通"],
            "性别": ["女", "男", "男", "女", "女", "男"],
            "产品类型": ["电子产品", "服装", "食品", "电子产品", "服装", "食品"],
            "总价": [299, 199, 89, 399, 259, 129],
            "评分": [4.5, 3.8, 4.2, 4.8, 3.9, 4.1]
        }
        df = pd.DataFrame(data).set_index("订单号")
    
    # 处理“时间”列，转换为datetime并提取小时
    df["小时数"] = pd.to_datetime(df["时间"], format="%H:%M:%S").dt.hour
    return df


def add_sidebar_func(df):
    # 构建侧边栏筛选器
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
    # 按“产品类型”分组计算总销售额（折线图展示）
    sales_by_product_line = df.groupby(by=["产品类型"])[["总价"]].sum().sort_values(by="总价")
    # 生成折线图（产品类型）
    fig_product_sales = px.line(
        sales_by_product_line,
        x=sales_by_product_line.index,
        y="总价",
        title="<b>按产品类型划分的销售额（折线图）</b>",
        markers=True,  # 显示数据点标记
        line_shape="linear"  # 线性折线
    )
    # 美化图表：调整字体和颜色
    fig_product_sales.update_layout(
        xaxis_title="产品类型",
        yaxis_title="销售额（RMB）",
        font=dict(family="SimHei", size=12)  # 支持中文显示
    )
    return fig_product_sales


def hour_chart(df):
    # 按“小时数”分组计算总销售额（折线图展示）
    sales_by_hour = df.groupby(by=["小时数"])[["总价"]].sum().reset_index()
    # 生成折线图（小时销售额，时间趋势更直观）
    fig_hour_sales = px.line(
        sales_by_hour,
        x="小时数",
        y="总价",
        title="<b>按小时数划分的销售额（折线图）</b>",
        markers=True,  # 显示数据点标记
        line_shape="spline"  # 平滑折线，更美观
    )
    # 美化图表：调整字体和颜色
    fig_hour_sales.update_layout(
        xaxis_title="小时数（24小时制）",
        yaxis_title="销售额（RMB）",
        font=dict(family="SimHei", size=12)  # 支持中文显示
    )
    return fig_hour_sales


def main_page_demo(df):
    # 设置页面标题和布局
    st.title("📊 销售仪表板（折线图版）")
    st.markdown("---")
    
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
    st.markdown("---")

    # 构建图表区（2个容器）
    left_chart_col, right_chart_col = st.columns(2)

    # 左侧：小时销售额折线图
    with left_chart_col:
        hour_fig = hour_chart(df)
        st.plotly_chart(hour_fig, use_container_width=True)

    # 右侧：产品类型销售额折线图
    with right_chart_col:
        product_fig = product_line_chart(df)
        st.plotly_chart(product_fig, use_container_width=True)


def run_app():
    # 设置页面配置
    st.set_page_config(
        page_title="销售仪表板（折线图）",
        page_icon="📈",
        layout="wide"
    )
    # 获取数据（增加异常处理，避免文件缺失报错）
    sale_df = get_dataframe_from_excel()
    # 侧边栏筛选
    df_selection = add_sidebar_func(sale_df)
    # 渲染主页面
    main_page_demo(df_selection)


if __name__ == "__main__":
    run_app()
