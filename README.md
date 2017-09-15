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

Optionally the output of `nodetool status` can be passed to include the node data size in the output.
```
python range.py token_ranges.log status.log
```


**Output**

```
Datacenter: Analytics
  
  10.0.0.1
    Rack: rack3
	Total Ranges: 3
	Primary: 
		Range: [8482013527982287894, 8612841500136256345]
		Range Size: 130827972153968451
		% of Mean: 0.37
	Secondary:
		Nodes: 10.0.0.2, 10.0.0.3
		Racks:
		  - rack1: 10.0.0.2
		  - rack2: 10.0.0.3
		Ranges: 
		  - 10.0.0.2: [8351185555828319443, 8482013527982287894]
		  - 10.0.0.3: [8220357583674350992, 8351185555828319443]
 
  ...
  
  Data Center Stats:
        Node Count: 10
        Mean Range Size:     207408463742901568
        Smallest Range Size: 739141085615637            (10.0.0.5)
        Largest Range Size:  18355649041246788292       (10.0.0.15)

```

**Output with `nodetool status` log included**

```
Datacenter: Analytics
  
  10.0.0.1
    Rack: rack3
	Total Ranges: 3
	Data Size: 245.3 GB
	Primary: 
		Range: [8482013527982287894, 8612841500136256345]
		Range Size: 130827972153968451
		% of Mean: 0.37
	Secondary:
		Nodes: 10.0.0.2, 10.0.0.3
		Racks:
		  - rack1: 10.0.0.2
		  - rack2: 10.0.0.3
		Ranges: 
		  - 10.0.0.2: [8351185555828319443, 8482013527982287894]
		  - 10.0.0.3: [8220357583674350992, 8351185555828319443]
 
  ...
  
  Data Center Stats:
        Node Count: 10
        Mean Range Size:     207408463742901568
        Smallest Range Size: 739141085615637            (10.0.0.5)
        Largest Range Size:  18355649041246788292       (10.0.0.15)

```

#### Current Limitations
- Works only with single token nodes