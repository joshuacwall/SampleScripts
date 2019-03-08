var margin = { top: 50, right: 350, bottom: 50, left: 100 },
    outerWidth = 1110,
    outerHeight = 500,
    width = outerWidth - margin.left - margin.right,
    height = outerHeight - margin.top - margin.bottom;

var x = d3.scale.linear()
    .range([0, width]).nice();

var y = d3.time.scale()
    .range([0, height]).nice();

var size_scale = d3.scale.linear()
    .range([0,100]) 

var xCat = "LIMIT_PRICE",
    yCat = "START_TIME",
    y2Cat = "END_TIME"
    wCat = "QUANTITY",
    colorCat = "SIDE";

var format = d3.time.format("%H:%M:%S");

d3.csv("Full.csv", function(data) {
  data.forEach(function(d) {
    d.LIMIT_PRICE = +d.LIMIT_PRICE;
    d.QUANTITY = +d.QUANTITY;
    d.SIDE = +d.SIDE;
    d.START_TIME = new Date(d.START_TIME / 1000);
    d.END_TIME = new Date(d.END_TIME / 1000);
    d["FIRST_REVISION_ORDER_ID"] = d["FIRST_REVISION_ORDER_ID"];
    d["DIRECTION"] = d["DIRECTION"];
    d["SECURITY_RIC"] = d["SECURITY_RIC"];
    d["PORTFOLIO"] = d["PORTFOLIO"];
    d["CLIENT_ID"] = d["CLIENT_ID"];
    d["TRANSACTION_DESTINATION"] = d["TRANSACTION_DESTINATION"];
    d.life = (d.END_TIME*1000 - d.START_TIME*1000);
  });

 
  x.domain(d3.extent(data, function(d){return d.LIMIT_PRICE;}));
  y.domain(d3.extent(data, function(d){return d.START_TIME;}));
  size_scale.domain(d3.extent(data, function(d){return d.QUANTITY;}));

  var xAxis = d3.svg.axis()
      .scale(x)
      .orient("top")
      .tickSize(height);

  var yAxis = d3.svg.axis()
      .scale(y)
      .orient("left")
      .tickSize(-width)
      .tickFormat(format);

  var color = d3.scale.category10();

  var tip = d3.tip()
      .attr("class", "d3-tip")
      .offset([-10, 0])
      .html(function(d) {
        return xCat + ": " + d.life + "<br>" + yCat + ": " + d[yCat] + "<br>" + wCat + ": " + d.END_TIME;
      });

  var zoomBeh = d3.behavior.zoom()
      .x(x)
      .y(y)
      //.scaleExtent([0, 500])
      .on("zoom", zoom);

  var svg = d3.select("#scatter")
    .append("svg")
      .attr("width", outerWidth)
      .attr("height", outerHeight)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
      .call(zoomBeh);

  svg.call(tip);

  svg.append("rect")
      .attr("width", width)
      .attr("height", height);

  svg.append("g")
      .classed("x axis", true)
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
    .append("text")
      .classed("label", true)
      .attr("x", width)
      .attr("y", -height - 30)
      .style("text-anchor", "end")
      .text(xCat)
      .style("font-weight","bold");

  svg.append("g")
      .classed("y axis", true)
      .call(yAxis)
    .append("text")
      .classed("label", true)
      .attr("transform", "rotate(-90)")
      .attr("y", -margin.left + 20)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text(yCat)
      .style("font-weight","bold");

  var objects = svg.append("svg")
      .classed("objects", true)
      .attr("width", width)
      .attr("height", height);

  objects.append("svg:line")
      .classed("axisLine hAxisLine", true)
      .attr("x1", 0)
      .attr("y1", 0)
      .attr("x2", width)
      .attr("y2", 0)
      .attr("transform", "translate(0,0)");

  objects.append("svg:line")
      .classed("axisLine vAxisLine", true)
      .attr("x1", 0)
      .attr("y1", 0)
      .attr("x2", 0)
      .attr("y2", height);

  objects.selectAll(".dot")
      .data(data)
    .enter().append("rect")
      .classed("dot", true)
      .attr("height", function (d) {return d.life;})
      .attr("width", function (d) {return size_scale(d.QUANTITY);} )
      .attr('transform', transform)
      .style("fill", function(d) { return color(d[colorCat]);})
      .on("mouseover", tip.show)
      .on("mouseout", tip.hide);

    var objects2 = svg.append("svg")
      .classed("objects", true)
      .attr("width", width)
      .attr("height", height);

    objects2.selectAll(".dot")
      .data(data)
      .enter().append("rect")
      .classed("dot", true)
      .attr("height", function (d) {return d.life;} )
      .attr("width", 5)
      .attr('transform', transform)
      .style("fill", "black");



/*   var legend = svg.selectAll(".legend")
      .data(color.domain())
    .enter().append("g")
      .classed("legend", true)
      .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

  legend.append("rect")
        .attr("height", 3.5)
         .attr("width", 3.5)
      .attr("fill", color);

  legend.append("text")
      .attr("x", width + 26)
      .attr("dy", ".35em")
      .text(function(d) { return d; }); */

  function zoom() {
    svg.select(".x.axis").call(xAxis);
    svg.select(".y.axis").call(yAxis);

    svg.selectAll(".dot")
        .attr("transform", transform);
  }


  function transform(d) {
    return "translate(" + x(d[xCat]) + "," + y(d[yCat]) + ")";
  }
});