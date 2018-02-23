# tools
utility command line scripts

## plot-json
This plots json data by matplotlib
```
$ plot-json x-axis y-axis path [path,...]
```

| option | description
|:-|:-|
| --window-size | window size of moving average |
| --inline | show graph on the terminal (only for MacOS) |
| --clipboard | copy graph image to clipboard (only for Ubuntu) |

### example
```
# test.json
{"step": 10, "reward: 1"}
{"step": 15, "reward: 0"}
{"step": 17, "reward: 0"}
```

```
$ plot-json step reward test.json
```
![figure_1](https://user-images.githubusercontent.com/5235131/36542707-ec7e06fe-1824-11e8-93e4-2c6cfeaf1b7c.png)

## echo-timestamp
This puts current timestamp into stdin. Use this for log name.
```
$ echo-timestamp
20180223191528 # no newline
```
