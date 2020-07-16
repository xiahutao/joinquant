var wsUri = "ws://127.0.0.1:1114/";
//var wsUri = "ws://121.36.157.1:1114/";
var output;
var no_show_list = ["客户号","股东代码","席位号","营业部号","主副标志","保本价格","当前成本","累计盈亏","昨日库存数量"];

function init() {
    output = document.getElementById("output");
    testWebSocket();
}

function testWebSocket() {
    websocket = new WebSocket(wsUri);
    websocket.binaryType = 'arraybuffer';
    websocket.onopen = function (evt) {
        onOpen(evt)
    };
    websocket.onclose = function (evt) {
        onClose(evt)
    };
    websocket.onmessage = function (evt) {
        onMessage(evt)
    };
    websocket.onerror = function (evt) {
        onError(evt)
    };
}

function sleep (time) {
    return new Promise((resolve) => setTimeout(resolve, time));
  }
  

async function onOpen(evt) {
    writeToScreen("CONNECTED");
    req_info('req_fund');
    await sleep(500);
    req_info('req_hold');
    await sleep(500);
    req_info('req_trades');
    await sleep(500);
    req_info('req_orders');
}

function req_info(req_cmd)
{
    let req_str = {
        'cmd': req_cmd
    };
    json_data = JSON.stringify(req_str);
    doSend(json_data);
}

function onClose(evt) {
    writeToScreen("DISCONNECTED");
}

function bolb2str(bolbdata) {
    var reader = new FileReader();
    var content;
    reader.onload = function (event) {
        content = reader.result; //内容就在这里
        //console.log("data:::");
        //console.log(content);
        return content;
    };
    console.log(reader.readAsText(bolbdata));
    return content;
}

function buf2str(buffer) {
    let encodedString = String.fromCodePoint.apply(null, new Uint8Array(buffer));
    let decodedString = decodeURIComponent(escape(encodedString)); //没有这一步中文会乱码
    return decodedString
}

function onMessage(evt) {
    array_buffer = evt.data;
    //console.log("arraybuffer:",array_buffer); //数字我看过了，确实是utf-8的编码
    //转换成json数据
    json_str = buf2str(array_buffer); // 转换成string 乱码
    json_data = JSON.parse(json_str);
    cmd = json_data['cmd'];
    cmd_data = JSON.stringify(json_data['data']);
    writeToScreen('<p">cmd: ' + cmd + '</p>');
    writeToScreen('<p">data: ' + cmd_data + '</p>');
    if(cmd == "OnFund"){json2table(json_data['data'],"fund_table");}
    if(cmd == "OnHold"){onHold(json_data['data']);}
    if(cmd == "OnTrades"){json2table(json_data['data'],"trades_table");}
    if(cmd == "OnOrders"){json2table(json_data['data'],"orders_table");}
    //websocket.close();
}

function onHold(hold_data)
{
    var html = "";
    $.each(hold_data, function (index, item) {
        if (index === 0) {
            html += "<tr>";
            // 表头
            $.each(item, function (vlaIndex) {
                if(IN(vlaIndex,no_show_list))return true;
                html += "<td>";
                html += vlaIndex;
                html += "</td>";
            });
            html += "<td>市场价</td>";
            html += "<td>盈亏比例</td>";
            html += "</tr>";
        }
        html += "<tr>";
        $.each(item, function (vlaIndex, valItem) {
            if(IN(vlaIndex,no_show_list))return true;
            html += "<td>";
            html += valItem;
            html += "</td>";
        });
        html += "<td>";
        html += (item["证券市值"]/item["当前拥股数量"]);
        html += "</td>";
        html += "<td>";
        var gain_pct = ((item["浮动盈亏"]/item["证券市值"])*100).toFixed(2);
        if(isNaN(gain_pct))
        {
            html += '0';
        }else{
            html += gain_pct.toString() +'%';
        }
        
        html += "</td>";
        html += "</tr>";
    });
    var table_dom = document.getElementById("hold_table");
    table_dom.innerHTML = html;
}

function onError(evt) {
    writeToScreen('<span style="color: red;">ERROR:</span> ' + evt.data);
}

function doSend(message) {
    writeToScreen("SENT: " + message);
    websocket.send(message);
}

function writeToScreen(message) {
    var pre = document.createElement("p");
    pre.style.wordWrap = "break-word";
    pre.innerHTML = message;
    output.appendChild(pre);
    //判断元素是否出现了滚动条
    output.scrollTop = output.scrollHeight;

}

window.addEventListener("load", init, false);

var IN = function(val,ls){
    return ls.indexOf(val) != -1;
}

function json2table(json_data, table_id) {
    //var no_show_list = ["客户号","股东代码","席位号","营业部"];
    var html = "";
    $.each(json_data, function (index, item) {
        if (index === 0) {
            html += "<tr>";
            // 表头
            $.each(item, function (vlaIndex) {
                if(IN(vlaIndex,no_show_list))return true;
                html += "<td>";
                html += vlaIndex;
                html += "</td>";
            });
            html += "</tr>";
        }
        html += "<tr>";
        $.each(item, function (vlaIndex, valItem) {
            if(IN(vlaIndex,no_show_list))return true;
            html += "<td>";
            html += valItem;
            html += "</td>";
        });
        html += "</tr>";
    });
    var table_dom = document.getElementById(table_id)
    table_dom.innerHTML = html;
}