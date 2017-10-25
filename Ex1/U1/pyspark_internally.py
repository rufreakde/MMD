

CODE:
rdd_a1
rdd_b2

rdd_a2 = rdd_a1.groupByKey(...)
rdd_b2 = rdd_b1.map(...).filter(...)

rdd_c = rdd_a2.join(rdd_b2)


WHAT IT DOES:

1) Runs generated Tasks graph

rdd_a2 holds the ref to a new rdd after the operation of groupByKey
rdd_b2 same shit
rdd_c => joined rdd ref of a1 and b2

2) Pipelines: Stages of the join:

	Stage1: save rdd_a1
	Stage2: save rdd_b2

3) cache awarnes:	
	caches inside the main memory not inside the ram
	
4) partitioning-awarnes:
	-after working with Data its reorganiszed
	-if the data is cached then we can just eassign it without a reorganization.


FROM THE TALK:
first video of lecutre 1 pp
