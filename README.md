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
	- Total Ranges: 2
	- Primary Range: [-8394794879879642285, -8263966907725673834]
	- Secondary Nodes: 10.0.10.4 (rack1)
	- Secondary Ranges: 
	    10.0.10.4: [-8493839785352138176, -8394794879879642285]

  
  10.0.10.5
	- Total Ranges: 4
	- Primary Range: [-3595551810977285504, -3554159910182809598]
	- Secondary Nodes: 10.0.10.6 (rack1), 10.0.10.3 (rack2), 10.0.10.8 (rack3)
	- Secondary Ranges: 
	    10.0.10.6: [-3684987882336778049, -3595551810977285504]
	    10.0.10.3: [-3946643826644714951, -3815815854490746500]
	    10.0.10.8: [-3815815854490746500, -3684987882336778049]

  ...
  Token range sizes:
        Largest size: 18355649041246788292
        Avg size: 207408463742901568
        Smallest size: 739141085615637
```

#### Current Limitations
- Works only with single token nodes