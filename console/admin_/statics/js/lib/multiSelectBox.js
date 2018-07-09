/**
 * Created by Yuwei.
 *
 * MultiSelectBox
 */

/* 使用案例
 * var $app = $("#app");
 * var box = new MultiSelectBox({
      container: $app, //用于生成插件的父元素
      leftTitle: "人员名单",
      rightTitle: "公开人员名单",
      isSearchable: true,
      event:{
        addListPreCallback:function(){},
        removeListPreCallback:function(){},
        addListCallback:function(){},
        removeListCallback:function(){}
      },
      dataList: [
        [{id: 1, value: 'data1', data: {}}, {id: 2, value: 'data2', data: {}}], // 左侧列表
        [{id: 3, value: 'data3', data: {}}, {id: 4, value: 'data4', data: {}}]  // 右侧列表
      ]
    });
 * box.addItem(1); // 用于下面获得变化列表用，一般通过UI界面操作。
 * box.removeItem(3); // 用于下面获得变化列表用，一般通过UI界面操作。
 * console.log(box.getChangedData()); // 获取变化列表
 * box.setData([
 *   [{id: 1, value: 'data1'}, {id: 2, value: 'data2'}], // 左侧列表
 *   [{id: 3, value: 'data3'}, {id: 4, value: 'data4'}]  // 右侧列表
 * ]);
 * console.log(box.getData("left")); // 获取左侧的最终列表
 */

define(function() {
  var MultiSelectBox = function(option) {
    this.leftTitleText = option.leftTitle;
    this.rightTitleText = option.rightTitle;
    this.isSearchable = option.isSearchable || true;
    this.leftBoxDataList = option.dataList[0] || [];
    this.rightBoxDataList = option.dataList[1] || [];
    this.event = option.event;

    this.leftBoxChangeList = [];
    this.rightBoxChangeList = [];

    this.initData();
    this.initEvent();
    this.obj = this.renderBox(option.container);

    this.initElement();


    this.listeningAddRemove();
    this.listeningSearch();
  };
  MultiSelectBox.prototype.initData = function() {
    this.leftBoxDataList.map(function(item) {
      if (!item.change) {
        item.change = false;
      }
      return item;
    });
    this.rightBoxDataList.map(function(item) {
      if (!item.change) {
        item.change = false;
      }
      return item;
    });
  };
  MultiSelectBox.prototype.initEvent = function() {
    var event = {
      addListPreCallback: function(id) {
        return true;
      },
      removeListPreCallback: function(id) {
        return true;
      },
      addListCallback: function(massage, id) {

      },
      removeListCallback: function(massage, id) {

      }
    };
    this.event = Object.assign(event, this.event);
  };
  MultiSelectBox.prototype.renderDataList = function(element, dataList, side) {
    var list = '';
    var fragment = document.createDocumentFragment();
    var unit = side === "left" ? '+' : '-';
    dataList.map(function(item) {
      fragment.appendChild($('<li data-id="' + item.id + '"><span>' + item.value + '</span><button>' + unit + '</button></li>').data('data',item.data)[0]);
    });
    element.find('ul').empty().append(fragment);
  };

  MultiSelectBox.prototype.renderBox = function(element) {
    var multiSelectBoxHTML = $('' +
      '<div class="multi-select-box">' +
      '  <div class="multi-select-box-half multi-select-box-left">' +
      '    <div class="multi-select-box-header multi-select-box-header-left">' +
      '      <h5></h5>' +
      '    </div>' +
      '    <div class="multi-select-box-content multi-select-box-content-left">' +
      '      <ul>' +
      '      </ul>' +
      '    </div>' +
      '  </div>' +
      '  <div class="multi-select-box-half multi-select-box-right">' +
      '    <div class="multi-select-box-header multi-select-box-header-right">' +
      '      <h5></h5>' +
      '    </div>' +
      '    <div class="multi-select-box-content multi-select-box-content-right">' +
      '      <ul>' +
      '      </ul>' +
      '    </div>' +
      '  </div>' +
      '</div>');


    element.html(multiSelectBoxHTML);

    return element;
  };

  MultiSelectBox.prototype.initElement = function() {

    this.leftHeader = this.obj.find(".multi-select-box-header-left");
    this.rightHeader = this.obj.find(".multi-select-box-header-right");

    this.leftBox = this.obj.find(".multi-select-box-left");
    this.rightBox = this.obj.find(".multi-select-box-right");

    this.leftTitle = this.leftHeader.find("h5");
    this.rightTitle = this.rightHeader.find("h5");

    this.leftTitle.text(this.leftTitleText);
    this.rightTitle.text(this.rightTitleText);

    var searchArea = '' +
      '<div class="multi-select-box-search">' +
      '  <div class="multi-select-box-search-input"><input type="text" class="multi-select-box-input" placeholder="请输入您要搜索的内容" /></div>' +
      '  <button class="multi-select-box-search-btn">搜</button>' +
      '</div>';

    if (this.isSearchable) {
      this.leftHeader.append($(searchArea));
      this.rightHeader.append($(searchArea));
    }

    this.leftSearchBtn = this.leftBox.find('.multi-select-box-search-btn');
    this.rightSearchBtn = this.rightBox.find('.multi-select-box-search-btn');

    this.leftInputBox = this.leftBox.find(".multi-select-box-input");
    this.rightInputBox = this.rightBox.find(".multi-select-box-input");

    // 用于整个插件的变量
    this.leftContent = this.obj.find(".multi-select-box-content-left");
    this.rightContent = this.obj.find(".multi-select-box-content-right");

    this.renderDataList(this.leftContent, this.leftBoxDataList, "left");
    this.renderDataList(this.rightContent, this.rightBoxDataList, "right");
  };

  MultiSelectBox.prototype.listeningAddRemove = function() {
    var _this = this;
    this.leftContent.on("click", "button", function() {
      var itemId = $(this).parent().data('id');
      var itemData = $(this).parent().data('data');
      if (_this.event.addListPreCallback(itemId, itemData)) {
        _this.addItem(itemId);
        _this.event.addListCallback('success', itemId);
      } else {
        _this.event.addListCallback('error', itemId);
      }
    });
    this.leftContent.on("dblclick", "li", function() {
      var itemId = $(this).data('id');
      var itemData = $(this).data('data');
      if (_this.event.addListPreCallback(itemId, itemData)) {
        _this.addItem(itemId);
        _this.event.addListCallback('success', itemId);
      } else {
        _this.event.addListCallback('error', itemId);
      }
    });
    this.rightContent.on("click", "button", function() {
      var itemId = $(this).parent().data('id');
      var itemData = $(this).parent().data('data');
      if (_this.event.removeListPreCallback(itemId, itemData)) {
        _this.removeItem(itemId);
        _this.event.removeListCallback('success', itemId);
      } else {
        _this.event.removeListCallback('error', itemId);
      }
    });
    this.rightContent.on("dblclick", "li", function() {
      var itemId = $(this).data('id');
      var itemData = (this).data('data');
      if (_this.event.removeListPreCallback(itemId, itemData)) {
        _this.removeItem(itemId);
        _this.event.removeListCallback('success', itemId);
      } else {
        _this.event.removeListCallback('error', itemId);
      }
    });
  };

  MultiSelectBox.prototype.addItem = function(id) {
    var selectedItem;
    var _this = this;
    this.leftBoxDataList.map(function(item, index) {
      if (item.id === id) {
        selectedItem = _this.leftBoxDataList.splice(index, 1)[0];
        selectedItem.change = !selectedItem.change;
        _this.leftBoxChangeList.push({
          type: "remove",
          data: selectedItem
        });
        _this.rightBoxChangeList.push({
          type: "add",
          data: selectedItem
        });
        _this.rightBoxDataList.push(selectedItem);
        _this.reloadChangeData();
      }
    });
    this.renderDataList(this.leftContent, this.leftBoxDataList, "left");
    this.renderDataList(this.rightContent, this.rightBoxDataList, "right");
  };

  MultiSelectBox.prototype.removeItem = function(id) {
    var selectedItem;
    var _this = this;
    this.rightBoxDataList.map(function(item, index) {
      if (item.id === id) {
        selectedItem = _this.rightBoxDataList.splice(index, 1)[0];
        selectedItem.change = !selectedItem.change;
        _this.leftBoxChangeList.push({
          type: "add",
          data: selectedItem
        });
        _this.rightBoxChangeList.push({
          type: "remove",
          data: selectedItem
        });
        _this.leftBoxDataList.push(selectedItem);
        _this.reloadChangeData();
      }
    });
    this.renderDataList(this.leftContent, this.leftBoxDataList, "left");
    this.renderDataList(this.rightContent, this.rightBoxDataList, "right");
  };

  MultiSelectBox.prototype.reloadChangeData = function() {
    var leftBoxChangeListNew = [];
    var rightBoxChangeListNew = [];
    this.leftBoxChangeList.forEach(function(item) {
      if (item.data.change) {
        leftBoxChangeListNew.push(item);
      }
    });
    this.rightBoxChangeList.forEach(function(item) {
      if (item.data.change) {
        rightBoxChangeListNew.push(item);
      }
    });
    this.leftBoxChangeList = leftBoxChangeListNew;
    this.rightBoxChangeList = rightBoxChangeListNew;
  };
  MultiSelectBox.prototype.listeningSearch = function() {
    var _this = this;

    this.leftSearchBtn.on("click", function() {
      var currentValue = _this.leftInputBox.val();
      _this.searchItem(currentValue, 'left');
    });

    this.rightSearchBtn.on("click", function() {
      var currentValue = _this.rightInputBox.val();
      _this.searchItem(currentValue, 'right');
    });

    this.leftInputBox.on("change", function() {
      if ($(this).val() === "") {
        _this.renderDataList(_this.leftBox, _this.leftBoxDataList, "left");
      }
    });
    this.rightInputBox.on("change", function() {
      if ($(this).val() === "") {
        _this.renderDataList(_this.rightBox, _this.rightBoxDataList, "right");
      }
    });
  };

  MultiSelectBox.prototype.searchItem = function(item, side) {
    var resultList = [];
    if (side === 'left') {
      this.leftBoxDataList.map(function(listItem) {
        if (listItem.value.indexOf(item) !== -1) {
          resultList.push(listItem);
        }
      });
      this.renderDataList(this.leftContent, resultList, "left");
    } else {
      this.rightBoxDataList.map(function(listItem) {
        if (listItem.value.indexOf(item) !== -1) {
          resultList.push(listItem);
        }
      });
      this.renderDataList(this.rightContent, resultList, "right");
    }
  };

  MultiSelectBox.prototype.setData = function(dataList) {
    this.leftBoxDataList = dataList[0];
    this.rightBoxDataList = dataList[1];
  };

  MultiSelectBox.prototype.setDataLeft = function(dataList) {
    this.leftBoxDataList = this.leftBoxDataList.concat(dataList);
    this.initData();
    this.renderDataList(this.leftContent, this.leftBoxDataList, "left");
  };

  MultiSelectBox.prototype.setDataRight = function(dataList) {
    this.rightBoxDataList = this.rightBoxDataList.concat(dataList);
    this.initData();
    this.renderDataList(this.rightContent, this.rightBoxDataList, "right");
  };

  // 返回列表，默认返回两边的列表
  MultiSelectBox.prototype.getData = function(type) {
    switch (type) {
      case "left":
        return this.leftBoxDataList;
        break;
      case "right":
        return this.rightBoxDataList;
        break;
      default:
        return [this.leftBoxDataList, this.rightBoxDataList];
        break;
    }
  };

  // 返回变化的数据，默认返回两边的变化列表
  MultiSelectBox.prototype.getChangedData = function(type) {
    switch (type) {
      case "left":
        return this.leftBoxChangeList;
        break;
      case "right":
        return this.rightBoxChangeList;
        break;
      default:
        return [this.leftBoxChangeList, this.rightBoxChangeList];
        break;
    }
  };
  return MultiSelectBox;
});