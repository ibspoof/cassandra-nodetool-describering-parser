## Cassandra nodetool describering Parser

Python script to parse output of `nodetool describering {keyspace}` to validate number of replica a node owns and a nodes secondary ranges and nodes it shares token ranges data with.

#### Usage
```
cat token_ranges.log| python range.py
```
or
```
python range.py token_ranges.log
```


**Output**

```
Datacenter: Analytics

  10.0.10.3
	- Total Ranges: 2
	- Primary Range: [-8394794879879642285, -8263966907725673834]
	- Secondary Nodes: 10.0.10.4
	- Secondary Ranges: [-8493839785352138176, -8394794879879642285]

  
  10.0.10.5
	- Total Ranges: 4
	- Primary Range: [-3595551810977285504, -3554159910182809598]
	- Secondary Nodes: 10.0.10.6, 10.0.10.3, 10.0.10.8
	- Secondary Ranges: [-3684987882336778049, -3595551810977285504], [-3946643826644714951, -3815815854490746500], [-3815815854490746500, -3684987882336778049]

```

#### Current Limitations
- Works only with single token nodes