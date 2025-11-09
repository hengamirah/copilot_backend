# Equipment and Tag Mapping for Historian Data

Each production unit or device in the milk plant corresponds to a tag pattern in the Historian table:

| Equipment Name | Tag Pattern | Description |
|-----------------|-------------|--------------|
| Skim milk outlet pump | Cluster1.Raw_SkimMilkOutPump_PM800% | Measures power/energy for the skim milk outlet pump |
| Full milk outlet pump | Cluster1.Raw_FullMilkOutPump_PM800% | Power and kWh usage for full milk outlet pump |
| Line 1 pasteurization unit | Cluster1.PLT_LINE1_PM800% | Represents pasteurizer line 1 (called 'PLT' in tags) |
| Line 2 pasteurization unit | Cluster1.PLT_LINE2_PM800% | Represents pasteurizer line 2 |
| Filling machine | Cluster1.Bottler_Filler_PM800% | Filling station power and kWh tags |
| Bottle labeling machine | Cluster1.Bottler_Label_PM800% | Labeling machine tags |
| Conveyor between filler and labeler | Cluster1.Bottler_Conveyor_PM800% | Conveyor line equipment |
| Bottle capping machine | Cluster1.Bottler_Cap_PM800% | Capping machine tags |
| Building electrical load | Cluster1.BLD_PM800% | Total building electrical meter |
| Energy tariff meter | Cluster1.Tariff | Tracks tariff information |
