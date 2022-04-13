# coding: utf-8
# author: Zhuoyan Luo

import os
import json
from py2neo import Graph,Node
from tqdm import tqdm

class MedicalGraphFromJson:
    def __init__(self):
        cur_dir = './'
        self.data_path = os.path.join(cur_dir, 'data')
        self.g = Graph(
            host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            port=7687,  # neo4j 服务器监听的端口号
            user="neo4j",  # 数据库user name，如果没有更改过，应该是neo4j
            password="zhuo123*",name='medicalgraph') #连接知识图谱
        self.rel_file='new_relations.json'
        self.node_file='new_entities.json'
        self.mapping = {
            'Disease':'疾病',
            'Drug':'药物',
            'Food':'食物',
            'Dish':'食谱',
            'Department':'二级科室',
            'Office':'一级科室',
            'Check':'检查手段',
            'Symptom':'症状',
            'Cure':'治疗方案',
            'Producer':'生产商',
        }#将英文label转换成中文形式
        self.propertys = {
        'name':'名称',
        'desc':'描述',
        'prevent':'预防方法',
        'cause':'病因',
        'easy_get':'易得人群',
        'cure_lasttime':'治疗时长',
        'cured_prob':'治愈概率'
        }

    def build_graph(self):
        res=self.build_nodes()
        if res==-1:
            print('no nodes file, can not create relations')
            return
        self.build_rels()

    def build_nodes(self):
        """
        Descirption:辅助建立节点函数
        """
        node_file=os.path.join(self.data_path,self.node_file)
        if not os.path.exists(node_file):
            return -1
        with open(node_file, encoding='UTF-8') as f:
            nodes=json.load(f)
        for node in tqdm(nodes, total=len(nodes), desc='create nodes'):
            self.create_node(node)
        return 0

    def create_node(self,node):
        """
        Description: 根据不同节点来编写不同的方式来建立实体节点
        """
        label=node['label']       
        if label != 'Disease':
            n=Node(self.mapping[label])
            n['名称'] = node['name']
        else:
            node = node['name']
            n = Node(self.mapping[label])
            for key,value in self.propertys.items():
                n[value] = node[key]

        self.g.create(n)

    def build_rels(self):
        """
        Description: 建立图谱的关系
        """
        rel_file=os.path.join(self.data_path,self.rel_file)
        if not os.path.exists(rel_file):
            print(self.rel_file,'not exist, skip')
            return
        with open(rel_file, encoding='UTF-8') as f:
            relations=json.load(f)
        for rel in tqdm(relations, total=len(relations), desc='create relations'):
            self.create_rel(rel)

    def create_rel(self,rels_set):
        """
        Description:创建关系函数，通过书写Cypher语句来导入关系
        """
        start_entity_type=rels_set['start_entity_type']
        end_entity_type=rels_set['end_entity_type']
        rel_type=rels_set['rel_type']
        rel_name=rels_set['rel_name']
        rels=rels_set['rels']
        for rel in rels:
            p=rel['start_entity_name']
            q=rel['end_entity_name']
            query = "match(p:%s),(q:%s) where p.名称='%s'and q.名称='%s' create (p)-[rel:%s {名称:'%s'}]->(q)" % (
                self.mapping[start_entity_type], self.mapping[end_entity_type], p, q,rel_name,rel_name)
            try:
                self.g.run(query)
            except Exception as e:
                print(e)
        return

if __name__ == '__main__':
    handler = MedicalGraphFromJson()
    handler.build_graph()
    print('finish')

