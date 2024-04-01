from pyvis.network import Network
import os, json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

indent = '  '

def makeTreemap(labels, parents):
    data = go.Treemap(
        ids=labels,
        labels=labels,
        parents=parents,
        root_color="lightgray")
    fig = go.Figure(data)
    return fig

def makeIcicle(labels, parents):
    data = go.Icicle(
        ids=labels,
        labels=labels,
        parents=parents,
        root_color="lightgrey")
    fig = go.Figure(data)
    return fig

def makeSunburst(labels, parents):
    data = go.Sunburst(
        ids=labels,
        labels=labels,
        parents=parents,
        insidetextorientation='horizontal')
    fig = go.Figure(data)
    return fig

def makeSankey(labels, parents):
    data = go.Sankey(
        node=dict(label=labels),
        link=dict(
            source=[list(labels).index(x) for x in labels],
            target=[-1 if pd.isna(x) else list(labels).index(x) for x in parents],
            label=labels,
            value=list(range(1, len(labels)))))
    fig = go.Figure(data)
    return fig


def getJson(df):

    # collect all nodes
    nodes = {}
    for _, row in df.iterrows():
        name = row.iloc[0]
        nodes[name] = { "name": name }

    # move children under parents, and detect root
    root = None
    for _, row in df.iterrows():
        node = nodes[row.iloc[0]]
        isRoot = pd.isna(row.iloc[1])
        if isRoot: root = node
        else:
            parent = nodes[row.iloc[1]]
            if "children" not in parent: parent["children"] = []
            parent["children"].append(node)

    return root

def makeCollapsibleTree(df):

    # create HTML file from template customized with our JSON
    with open(f"animated/templates/collapsible-tree.html", "r") as file:
        content = file.read()
        
    root = getJson(df)
    filename = f'animated/collapsible-tree.html'
    with open(filename, "w") as file:
        file.write(content.replace('"{{data}}"', json.dumps(root, indent=4)))
    return os.path.abspath(filename)

def makeNetworkGraph(df):

    data = Network(notebook=True, heading='')
    data.barnes_hut(
        gravity=-80000,
        central_gravity=0.3,
        spring_length=10.0,
        spring_strength=1.0,
        damping=0.09,
        overlap=0)

    for _, row in df.iterrows():
        src = str(row.iloc[0])
        dst = str(row.iloc[1])
        data.add_node(src)
        data.add_node(dst)
        data.add_edge(src, dst)

    # set node size to number of child nodes
    map = data.get_adj_list()
    for node in data.nodes:
        node["value"] = len(map[node["id"]])

    filename = "animated/network-graph.html"
    data.show(filename)
    return os.path.abspath(filename)

st.set_page_config(layout="wide")
st.title("Snowflake Object Hierarchy")

df = pd.read_csv("data/databaseobject.csv", header=0).convert_dtypes()

labels, parents = df[df.columns[0]], df[df.columns[1]]

t0,t1, t2, t3, t4,t5,t6 = st.tabs(["Hiearchy","Treemap", "Icicle", "Sunburst", "Sankey","Collapsible Tree", "Network Graph"])

with t0:
    st.dataframe(df)

with t1:
    fig = makeTreemap(labels, parents)
    st.plotly_chart(fig, use_container_width=True)

fig = makeIcicle(labels, parents)
t2.plotly_chart(fig, use_container_width=True)

with t3:
    fig = makeSunburst(labels, parents)
    st.plotly_chart(fig, use_container_width=True)

with t4:
    fig = makeSankey(labels, parents)
    st.plotly_chart(fig, use_container_width=True)

with t5:
    with open(makeCollapsibleTree(df), 'r', encoding='utf-8') as f:
        components.html(f.read(), height=2200, width=1000)
with t6:
    with open(makeNetworkGraph(df), 'r', encoding='utf-8') as f:
        components.html(f.read(), height=2200, width=1000)