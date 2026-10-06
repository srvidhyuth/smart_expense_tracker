const API_URL = '/api/expenses';

// DOM Elements
const expenseForm = document.getElementById('expense-form');
const expenseIdInput = document.getElementById('expense-id');
const dateInput = document.getElementById('expense-date');
const descInput = document.getElementById('expense-desc');
const amountInput = document.getElementById('expense-amount');
const categoryInput = document.getElementById('expense-category');
const submitBtn = document.getElementById('submit-btn');
const cancelEditBtn = document.getElementById('cancel-edit');
const formTitle = document.getElementById('form-title');
const expenseList = document.getElementById('expense-list');
const totalAmountDisplay = document.getElementById('total-amount');
const categorySummary = document.getElementById('category-summary');
const toast = document.getElementById('toast');

// Category Colors for UI
const categoryColors = {
    'Food': '#f59e0b',
    'Transport': '#3b82f6',
    'Entertainment': '#ec4899',
    'Utilities': '#06b6d4',
    'Shopping': '#8b5cf6',
    'Health': '#10b981',
    'Other': '#94a3b8'
};

// State
let expenses = [];
let isEditing = false;

// Format Currency
const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
};

// Show Toast Notification
const showToast = (message, type = 'success') => {
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
};

// Initial Load
const loadExpenses = async () => {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error('Failed to fetch expenses');
        
        expenses = await response.json();
        renderExpenses();
        updateSummary();
    } catch (error) {
        showToast(error.message, 'error');
    }
};

// Set Default Date
const setDefaultDate = () => {
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
};

// Add or Update Expense
expenseForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const expenseData = {
        date: dateInput.value,
        description: descInput.value,
        amount: parseFloat(amountInput.value),
        category: categoryInput.value
    };

    try {
        if (isEditing) {
            const id = expenseIdInput.value;
            const response = await fetch(`${API_URL}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(expenseData)
            });
            
            if (!response.ok) throw new Error('Failed to update expense');
            showToast('Expense updated successfully');
            resetForm();
        } else {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(expenseData)
            });
            
            if (!response.ok) throw new Error('Failed to add expense');
            showToast('Expense added successfully');
            resetForm();
        }
        
        loadExpenses();
    } catch (error) {
        showToast(error.message, 'error');
    }
});

// Edit Expense
const editExpense = (id) => {
    const expense = expenses.find(exp => exp._id === id);
    if (!expense) return;
    
    isEditing = true;
    expenseIdInput.value = expense._id;
    dateInput.value = expense.date;
    descInput.value = expense.description;
    amountInput.value = expense.amount;
    categoryInput.value = expense.category;
    
    formTitle.textContent = 'Edit Expense';
    submitBtn.textContent = 'Update Expense';
    cancelEditBtn.style.display = 'block';
    
    // Scroll to form
    expenseForm.scrollIntoView({ behavior: 'smooth' });
};

// Cancel Edit
cancelEditBtn.addEventListener('click', () => {
    resetForm();
});

// Delete Expense
const deleteExpense = async (id) => {
    if (!confirm('Are you sure you want to delete this expense?')) return;
    
    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete expense');
        showToast('Expense deleted successfully');
        loadExpenses();
    } catch (error) {
        showToast(error.message, 'error');
    }
};

// Reset Form
const resetForm = () => {
    isEditing = false;
    expenseForm.reset();
    expenseIdInput.value = '';
    setDefaultDate();
    
    formTitle.textContent = 'Add New Expense';
    submitBtn.textContent = 'Add Expense';
    cancelEditBtn.style.display = 'none';
};

// Render Expenses to Table
const renderExpenses = () => {
    expenseList.innerHTML = '';
    
    if (expenses.length === 0) {
        expenseList.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; color: var(--text-muted);">No expenses found. Add one above!</td>
            </tr>
        `;
        return;
    }
    
    expenses.forEach(exp => {
        const tr = document.createElement('tr');
        
        const catColor = categoryColors[exp.category] || categoryColors['Other'];
        
        tr.innerHTML = `
            <td>${exp.date}</td>
            <td>${exp.description}</td>
            <td>
                <span class="category-badge" style="color: ${catColor}; border: 1px solid ${catColor}40;">
                    ${exp.category}
                </span>
            </td>
            <td class="amount">${formatCurrency(exp.amount)}</td>
            <td>
                <div class="action-btns">
                    <button class="btn-icon edit" onclick="editExpense('${exp._id}')" title="Edit">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                    </button>
                    <button class="btn-icon delete" onclick="deleteExpense('${exp._id}')" title="Delete">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                </div>
            </td>
        `;
        
        expenseList.appendChild(tr);
    });
};

// Update Summary Panel
const updateSummary = () => {
    // Total
    const total = expenses.reduce((sum, exp) => sum + exp.amount, 0);
    totalAmountDisplay.textContent = formatCurrency(total);
    
    // Category Breakdown
    const catTotals = {};
    expenses.forEach(exp => {
        catTotals[exp.category] = (catTotals[exp.category] || 0) + exp.amount;
    });
    
    categorySummary.innerHTML = '';
    
    // Sort categories by amount
    const sortedCats = Object.keys(catTotals).sort((a, b) => catTotals[b] - catTotals[a]);
    
    sortedCats.forEach(cat => {
        const amount = catTotals[cat];
        const catColor = categoryColors[cat] || categoryColors['Other'];
        
        const div = document.createElement('div');
        div.className = 'category-item';
        div.innerHTML = `
            <div class="cat-name">
                <span class="cat-color" style="background-color: ${catColor}"></span>
                <span>${cat}</span>
            </div>
            <span>${formatCurrency(amount)}</span>
        `;
        
        categorySummary.appendChild(div);
    });
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setDefaultDate();
    loadExpenses();
});
