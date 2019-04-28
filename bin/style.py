STYLE = """
            QCheckBox { spacing: 10px; height: 35px;}
            QCheckBox::indicator {width: 20px;height: 20px;}
            QCheckBox::indicator:unchecked {image:url(res/check_unsel.png);}
            QCheckBox::indicator:checked {image:url(res/check_sel.png);}

            QLineEdit {height: 30px;
                       font: 15px;
                       border:1px solid #D7D7D7;
                       selection-color: white;
                       margin: 2px;
            }
            QLabel {
                    height: 30px;
                    font: 15px;
            }
            QPushButton {height: 30px;
                         background-color:#FFFFFF;
                         border:1px solid #A5A5A5;
                         padding-left:15px;
                         padding-right:15px;
            }   
            QPushButton:hover {
                               color: #4BAEB3;
            }  
            QTreeWidget{
                      border: 1px solid #A0A0A0;
                      border-style: solid solid solid solid;
            }

            QTreeWidget::item{
                            height: 30px;
                            border: 1px solid #DDDDDD;
                            border-style: solid none none none;
                            color: black;
                            padding: 0px;

            }
            QTreeWidget::item:hover{
                            background: #EDF7F8;
            }
            QTreeWidget::item:selected{
                            background: #E2F2F3;
                            border: 1px solid #4BAEB3;
                            border-style: solid none solid none;

            }
            QTreeWidget::branch:selected{
                                       outline: none;
            }
            QHeaderView{
                        border: none;
                        font-size: 14px;
                        Font: Roman times;
                        color: black;
            }
            QHeaderView::section:hover{
                                       background-color:#FFFFFF;
                                       border: none;
                                       padding: 4px;
            }
    """
