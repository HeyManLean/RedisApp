# mongodb 设计数据库 schema

## 1. 商品文档

```js
{
    _id: ObjectId("4c4b1476238d3d4dd5003981"),
    slug: "wheelbarrow-9092",  // 唯一标识
    sku: "9092",  // 库存单位
    name: "Extra Large Wheelbarrow",
    description: "Heavy duty Wheelbarrow...",
    details: {
        weight: 47,
        weight_units: "lbs",
        model_num: 4039283402,
        manufacturer: "Acme",
        color: "Green"
    },
    total_reviews: 4,  // 查看次数
    average_review: 4.5,  // 平均查看时长
    pricing: {  // 价格
        retail: 589700,
        sale: 489700
    },
    price_history: [
        {
            retail: 529700,
            sale: 429700,
            start: new Date(2010, 4, 1),
            end: new Date(2010, 4, 8)
        },
        {
            retail: 529700,
            sale: 529700,
            start: new Date(2010, 4, 9),
            end: new Data(2010, 4, 16)
        }
    ],
    primary_category: ObjectId("6d5b1476238d3b4dd5000048"),  // 多对一关系
    cateogory_ids: [  // 多对多关系
        ObjectId("6a5b147238d3b4dd5000048"),
        ObjectId("6a5b147238d3b4dd5000049"),
    ],
    main_cat_id: ObjectId("6a5d1476238d3b4dd500048"),
    tags: ["tools", "gardening", "soil"]
}
```

## 2. 类别文档

```js
{
    _id: ObjectId("6a5b1476238d4b4dd5000048"),
    slug: "gardening-tools",
    name: "Gardenging Tools",
    description: "Gardeing gadgets galore!",
    parent_id: ObjectId("55804822812cb33678728f9"),  // 多对一关系
    ancestors: [
        {
            name: "Home",
            _id: ObjectId("558048f0812cb336b78728fa"),
            slug: "home"
        },
        {
            name: "Outdoors",
            _id: ObjectId("558048f0812cb336b78728f9"),
            slug: "outdoors"
        }
    ]
}
```

## 3. 订单文档

```js
{
    _id: ObjectId("6a5b1476238d4b4dd5000048"),
    user_id: ObjectId("6a5b1476238d4b4dd50008d44"),
    state: "CART",
    line_items: [
        {
            _id: ObjectId("6a5b1476238d4b4dd500dd33"),
            sku: "9092",
            name: "Extra Large Wheelbarrow",
            quantity: 1,
            pricing: {
                retail: 5897,
                sale: 4897,
            }
        }
        {
            _id: ObjectId("6a5b1476238d4b4dd5003982"),
            sku: "10027",
            name: "Rubberized Work Glove, Black",
            quantity: 2,
            pricing: {
                retail: 1499,
                sale: 1299,
            }
        }
    ],
    shipping_address: {
        street: "588 5th Street",
        city: "Brooklyn",
        state: "NY",
        zip: 11215
    },
    sub_total: 6196
}
```

4. 用户文档

```js
{
    _id: ObjectId("6a5b1476238d4b4dd50008d44"),
    username: "kbanker",
    email: "kylebanker@gmail.com",
    first_name: "Kyle",
    last_name: "Banker",
    hashed_password: "bd1cfa194c3a603e7186780824b04419",
    addresses: [
        {
            name: "home",
            street: "588 5th Street",
            city: "Brooklyn",
            state: "NY",
            zip: 11215
        },
        {
            name: "work",
            street: "1 E. 23rd Street",
            city: "New York",
            state: "NY",
            zip: 10010
        }
    ],
    payment_methods: [
        {
            name: "VISA",
            payment_token: "43f6ba1dfda6b8106dc7"
        }
    ]
}
```


5. 评价文档

```js
{
    _id: ObjectId("4c4b1476238d3b4dd5000041"),
    product_id: ObjectId("4c4b1476238d3b4dd5003981"),
    date: new Date(2010, 5, 7),
    title: "Amazing",
    text: "Has a squeaky wheel, but still a darn good wheelbarrow.",
    rating: 4,
    user_id: ObjectId("6a5b1476238d4b4dd50004239"),,
    username: "dgreenthumb",
    helpful_votes: 3,
    voter_ids: [
        ObjectId("4c4b1476238d3b4dd5000033"),
        ObjectId("7a4f1476238d3b4dd5000003"),
        ObjectId("92c21476238d3b4dd5000032")
    ]
}
```