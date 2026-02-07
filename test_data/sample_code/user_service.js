/**
 * User service module for managing user data.
 * This module provides CRUD operations for users.
 */

class UserService {
    /**
     * Create a new UserService instance.
     * @param {Object} database - Database connection object
     */
    constructor(database) {
        this.db = database;
        this.cache = new Map();
    }

    /**
     * Get a user by their ID.
     * @param {string} userId - The user's unique identifier
     * @returns {Promise<Object>} User object
     */
    async getUser(userId) {
        // Check cache first
        if (this.cache.has(userId)) {
            return this.cache.get(userId);
        }

        const user = await this.db.query('SELECT * FROM users WHERE id = ?', [userId]);

        // Cache the result
        if (user) {
            this.cache.set(userId, user);
        }

        return user;
    }

    /**
     * Create a new user.
     * @param {Object} userData - User data object
     * @param {string} userData.email - User's email address
     * @param {string} userData.name - User's full name
     * @param {string} userData.password - User's hashed password
     * @returns {Promise<Object>} Created user object
     */
    async createUser(userData) {
        const { email, name, password } = userData;

        // Validate required fields
        if (!email || !name || !password) {
            throw new Error('Missing required user data');
        }

        // Check if user already exists
        const existing = await this.db.query('SELECT * FROM users WHERE email = ?', [email]);
        if (existing) {
            throw new Error('User with this email already exists');
        }

        // Create the user
        const result = await this.db.insert('users', {
            email,
            name,
            password,
            created_at: new Date()
        });

        return result;
    }

    /**
     * Update an existing user.
     * @param {string} userId - The user's unique identifier
     * @param {Object} updates - Fields to update
     * @returns {Promise<Object>} Updated user object
     */
    async updateUser(userId, updates) {
        const user = await this.getUser(userId);

        if (!user) {
            throw new Error('User not found');
        }

        const result = await this.db.update('users', userId, updates);

        // Invalidate cache
        this.cache.delete(userId);

        return result;
    }

    /**
     * Delete a user by ID.
     * @param {string} userId - The user's unique identifier
     * @returns {Promise<boolean>} True if deleted successfully
     */
    async deleteUser(userId) {
        const result = await this.db.delete('users', userId);

        // Remove from cache
        this.cache.delete(userId);

        return result;
    }

    /**
     * Search users by criteria.
     * @param {Object} criteria - Search criteria
     * @param {number} limit - Maximum number of results
     * @returns {Promise<Array>} Array of user objects
     */
    async searchUsers(criteria, limit = 10) {
        const results = await this.db.query(
            'SELECT * FROM users WHERE name LIKE ? OR email LIKE ? LIMIT ?',
            [`%${criteria}%`, `%${criteria}%`, limit]
        );

        return results;
    }

    /**
     * Clear the user cache.
     */
    clearCache() {
        this.cache.clear();
    }
}

module.exports = UserService;
