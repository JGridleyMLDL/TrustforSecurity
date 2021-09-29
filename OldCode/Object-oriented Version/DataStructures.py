

Note: the data item is a tuple.


1) "Domain DS"
For calculating the Domain:
    list(index: data_item) -> set(possible_values)

    Domain - -> For each data_item -> the set of possibilites of values


2) "Source List"
For calculating alpha and p(C_wdv=1):

    2d-List:
    list - -> DataItems/Sources as index -> set(values)
    list[Source][Data_item]=set(value)

This removes the extractor and only includes each value once.


3) "p(V_d | X_d) List"
For storing the p(V_d=v | X_d):

    list - -> data_item as index - -> map(value): p(V_d=v | X_d)


4) "C_wdv List"
For storing C_wdv

    2d-List:
    # In notes, something about "List of p(C_wdv = 1)"?
    list - -> DataItems/Sources as index -> map(value) -> p(C_wdv=1)
    list[Source][Data_item][Value]=p(C_wdv=1)
Extends the source list to include the probability of C_wdv


5) "Accuracy List"
Storing A_w - -  2D list
    list[source][A_w value]     # Check this one - "Web Source 2D List"


6) "Alpha List"
Storing the alpha value
    2D list - -> Web Source - -> Data item - -> Map(value)=alpha value
