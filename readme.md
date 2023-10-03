# DBLP query server

## Goal

Given an author ID
> <https://dblp.org/pid/m/AndrewMcCallum>

Construct author info with publications as an XML record, e.g.,

```
    <dblpperson name="Andrew McCallum" pid="m/AndrewMcCallum" n="408">
      <person key="homepages/m/AndrewMcCallum" mdate="2022-11-02">
        <author pid="m/AndrewMcCallum">Andrew McCallum</author>
        <note type="affiliation">University of Massachusetts Amherst, USA</note>
        <url>http://www.cs.umass.edu/~mccallum/</url>
        <url>https://dl.acm.org/profile/81100553872</url>
      </person>
      <r>
        <inproceedings key="conf/acl/ChangSRM23" mdate="2023-08-10">
          <author pid="130/1022">Haw-Shiuan Chang</author>
          <author pid="301/6251">Ruei-Yao Sun</author>
          <author pid="331/1034">Kathryn Ricci</author>
          <author pid="m/AndrewMcCallum">Andrew McCallum</author>
          <title>Multi-CLS BERT: An Efficient Alternative to Traditional Ensembling.</title>
          <year>2023</year>
        </inproceedings>
      </r>
      ...
    </dblpperson>
```


## Setup
### Apache Jena
Run server:
> apache-jena-fuseki-4.9.0/fuseki-server --loc data/dataForTDB /ds
