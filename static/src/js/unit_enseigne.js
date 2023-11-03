odoo.define('amelioration_cnam.form_widgets', function (require) {
"use strict";

var core = require('web.core');
var FieldSelection = core.form_widget_registry.get('selection');

var MySelection = FieldSelection.extend({
    // add events to base events of FieldSelection
    events: _.defaults({
        // we will change of visibility on focus of field
        'focus select': 'onFocus'
    }, FieldSelection.prototype.events),
    onFocus: function() {
      print('heelllloooooooo!!!!!!!!!!!!!!!!!!!!')
      if (
          this.field_manager.ue_state.get_value() == "pre-inscription" &&
          this.field_manager.is_allowed_group_user.get_value() == true
      ){
          this.$el.find('pre-inscription').hide();
          this.$el.find('account').hide();
          this.$el.find('enf').hide();
          this.$el.find('cancel').hide();
      } 
      else if (
          this.field_manager.ue_state.get_value() == "accueil" &&
          this.field_manager.is_allowed_group_user.get_value() == true
      ) {
          this.$el.find('pre-inscription').hide();
          this.$el.find('accueil').hide();
          this.$el.find('enf').hide();
          this.$el.find('cancel').hide();
      } 
      else if (
          this.field_manager.ue_state.get_value() == "account" &&
          this.field_manager.is_allowed_group_user.get_value() == true
      ) {
          this.$el.find('pre-inscription').hide();
          this.$el.find('accueil').hide();
          this.$el.find('account').hide();
          this.$el.find('cancel').hide();
      } 
    }
});

// register your widget
core.form_widget_registry.add('select_custom_widget', MySelection);
});