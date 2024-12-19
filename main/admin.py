# admin.py
from django.contrib import admin
from .models import Transaction
from simple_history.admin import SimpleHistoryAdmin  # For history tracking

@admin.register(Transaction)
class TransactionAdmin(SimpleHistoryAdmin):  # Using SimpleHistoryAdmin for history
    # Columns to display in the list view
    list_display = ('mpesa_code', 'amount', 'phone_number', 'status', 'checkout_id')
    
    # Fields to filter by in the sidebar
    list_filter = ('status',)
    
    # Fields that are searchable in the admin interface
    search_fields = ('mpesa_code', 'phone_number', 'checkout_id')
    
    # Make some fields read-only
    readonly_fields = ('checkout_id', 'mpesa_code', 'amount')
    
    # Group fields into sections for better organization
    fieldsets = (
        ("Transaction Details", {
            'fields': ('amount', 'checkout_id', 'mpesa_code', 'status')
        }),
        ("Customer Details", {
            'fields': ('phone_number',)
        }),
    )
    
    # Custom actions
    actions = ['mark_as_verified']

    # Define custom action to mark transactions as Verified
    def mark_as_verified(self, request, queryset):
        updated = queryset.update(status='Verified')
        self.message_user(request, f"{updated} transactions marked as Verified.")
    mark_as_verified.short_description = "Mark selected transactions as Verified"
